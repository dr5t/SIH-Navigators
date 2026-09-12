import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from ml.models.speed_model import SpeedModel, export_torchscript

def train_model(epochs=5, batch_size=32, seq_len=200):
    """Simple training loop with dummy data to verify functionality."""
    model = SpeedModel(seq_len=seq_len)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    # Dummy dataset
    x_dummy = torch.randn(100, 6, seq_len)
    y_dummy = torch.randn(100, 1) * 10.0  # Speeds around 0-10 m/s
    loader = DataLoader(TensorDataset(x_dummy, y_dummy), batch_size=batch_size, shuffle=True)
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for x, y in loader:
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
    print("Training complete.")
    export_torchscript(model, "speed_model.pt", seq_len=seq_len)
    print("Model exported to speed_model.pt")

if __name__ == "__main__":
    train_model()
