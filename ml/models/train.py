import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

from ml.models.speed_model import SpeedModel
from ml.datasets.io_vnbd import list_sessions, IOVNBDParser
from ml.preprocessing.sync import synchronize_sensors
from ml.preprocessing.features import FeatureExtractor
from ml.datasets.split import split_sessions
from ml.models.baseline import KinematicBaseline, evaluate_baseline

def load_and_preprocess(sessions, target_hz=100.0, seq_len=200, stride=50):
    all_X = []
    all_y = []
    fe = FeatureExtractor(seq_len=seq_len, stride=stride)
    
    for session in sessions:
        parser = IOVNBDParser(session)
        try:
            imu, gnss = parser.load_all()
            _, s_imu, s_speed = synchronize_sensors(imu, gnss, target_hz)
            X, y = fe.create_windows(s_imu, s_speed)
            if len(X) > 0:
                all_X.append(X)
                all_y.append(y)
        except Exception as e:
            print(f"Skipping session {session}: {e}")
            
    if not all_X:
        return np.empty((0, 6, seq_len)), np.empty(0)
        
    return np.vstack(all_X), np.concatenate(all_y)

def evaluate_model(model: nn.Module, loader: DataLoader, criterion) -> float:
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for x, y in loader:
            out = model(x)
            loss = criterion(out, y)
            total_loss += loss.item() * len(y)
            all_preds.append(out.numpy())
            all_targets.append(y.numpy())
            
    if len(all_preds) == 0:
        return 0.0
        
    preds = np.concatenate(all_preds).flatten()
    targets = np.concatenate(all_targets).flatten()
    
    mae = np.mean(np.abs(preds - targets))
    rmse = np.sqrt(np.mean((preds - targets)**2))
    
    print(f"Validation - MAE: {mae:.2f} m/s, RMSE: {rmse:.2f} m/s")
    return total_loss / len(targets)

def train_pipeline(data_dir: str = "ml/data/io_vnbd", epochs: int = 10, batch_size: int = 32):
    print("--- AI Vehicle Speed Training Pipeline ---")
    
    sessions = list_sessions(data_dir)
    if not sessions:
        print("CRITICAL: No IO-VNBD datasets found. Aborting training.")
        return
        
    train_sess, val_sess, test_sess = split_sessions(sessions)
    print(f"Sessions -> Train: {len(train_sess)}, Val: {len(val_sess)}, Test: {len(test_sess)}")
    
    print("Loading and preprocessing data...")
    X_train, y_train = load_and_preprocess(train_sess)
    X_val, y_val = load_and_preprocess(val_sess)
    X_test, y_test = load_and_preprocess(test_sess)
    
    if len(X_train) == 0:
        print("CRITICAL: No valid training windows extracted. Aborting training.")
        return
        
    print(f"Extracted Windows -> Train: {len(X_train)}, Val: {len(X_val)}")
    
    # Baseline Eval
    print("Evaluating Kinematic Baseline on Validation set...")
    baseline = KinematicBaseline()
    baseline_preds = baseline.predict(np.transpose(X_val, (0, 2, 1))) # (N, C, L) -> (N, L, C)
    evaluate_baseline(baseline_preds, y_val)
    
    # PyTorch Setup
    train_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train).unsqueeze(1)), 
        batch_size=batch_size, shuffle=True
    )
    val_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val).unsqueeze(1)), 
        batch_size=batch_size, shuffle=False
    )
    
    model = SpeedModel(seq_len=200)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    # Training Loop
    best_val_loss = float('inf')
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        
        for x, y in train_loader:
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(y)
            
        train_loss /= len(X_train)
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}")
        
        val_loss = evaluate_model(model, val_loader, criterion)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "ml/models/best_speed_model.pth")
            
    print("Training complete.")

if __name__ == "__main__":
    train_pipeline()
