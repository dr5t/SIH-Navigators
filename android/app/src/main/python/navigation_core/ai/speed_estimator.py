import os
import time
import json
import numpy as np
from typing import Optional, Tuple

class AISpeedEstimator:
    def __init__(self, model_filename: str = "speed_model.pt", metadata_filename: str = "speed_metadata.json"):
        # Resolve path relative to this script so it works on Android (Chaquopy)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # go up from navigation_core/ai to python root
        self.model_path = os.path.join(base_dir, model_filename)
        self.metadata_path = os.path.join(base_dir, metadata_filename)
        
        self.is_available = False
        self.model = None
        self.model_version = "unknown"
        
        # Parity Config Defaults
        self.seq_len = 200
        self.accel_mean = np.array([0.0, 0.0, 9.8])
        self.accel_std = np.array([2.0, 2.0, 2.0])
        self.gyro_mean = np.array([0.0, 0.0, 0.0])
        self.gyro_std = np.array([0.5, 0.5, 0.5])
        
        self._load_metadata()
        self._load_model()
        
    def _load_metadata(self):
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    meta = json.load(f)
                    self.seq_len = meta.get("seq_len", 200)
                    norm = meta.get("normalization", {})
                    if "accel_mean" in norm: self.accel_mean = np.array(norm["accel_mean"])
                    if "accel_std" in norm: self.accel_std = np.array(norm["accel_std"])
                    if "gyro_mean" in norm: self.gyro_mean = np.array(norm["gyro_mean"])
                    if "gyro_std" in norm: self.gyro_std = np.array(norm["gyro_std"])
                    self.model_version = meta.get("version", "v1.0")
            except Exception as e:
                print(f"Failed to load AI metadata: {e}. Using defaults.")

    def _load_model(self):
        try:
            import torch
            if os.path.exists(self.model_path):
                # Ensure no forward-compatibility warnings break loading in newer pythons
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.model = torch.jit.load(self.model_path)
                self.model.eval()
                self.is_available = True
        except ImportError:
            print("PyTorch not found. AI Speed Estimator unavailable (falling back to kinematics).")
        except Exception as e:
            print(f"Failed to load AI model from {self.model_path}: {e}")

    def normalize(self, imu_window: np.ndarray) -> np.ndarray:
        """Exact parity with ml/preprocessing/features.py normalize()"""
        norm_data = np.copy(imu_window)
        norm_data[:, 0:3] = (norm_data[:, 0:3] - self.accel_mean) / self.accel_std
        norm_data[:, 3:6] = (norm_data[:, 3:6] - self.gyro_mean) / self.gyro_std
        return norm_data

    def estimate_speed(self, accel_window: np.ndarray, gyro_window: np.ndarray) -> Tuple[Optional[float], float]:
        """
        Estimates speed from IMU windows.
        Returns:
            (speed_m_s, confidence_0_to_1)
        """
        if not self.is_available or self.model is None:
            return None, 0.0
            
        try:
            import torch
            
            # 1. Combine
            if len(accel_window) != self.seq_len or len(gyro_window) != self.seq_len:
                return None, 0.0 # Window incomplete
                
            imu_window = np.hstack((accel_window, gyro_window)) # (SeqLen, 6)
            
            # 2. Normalize (Exact Parity)
            norm_imu = self.normalize(imu_window)
            
            # 3. Shape for Model: (Batch, Channels, SeqLen) -> (1, 6, 200)
            X = np.expand_dims(np.transpose(norm_imu, (1, 0)), axis=0)
            tensor_X = torch.from_numpy(X).float()
            
            # 4. Inference
            start_time = time.time()
            with torch.no_grad():
                pred = self.model(tensor_X).numpy()[0, 0]
            latency_ms = (time.time() - start_time) * 1000.0
            
            # 5. Quality/Confidence calculation (placeholder heuristic based on latency and sensible bounds)
            # True confidence would require a probabilistic model (e.g. MC Dropout or NLL output).
            confidence = 1.0
            if pred < 0 or pred > 60: # Unrealistic speed
                confidence = 0.1
                pred = max(0.0, pred)
                
            # Log latency in debug mode (print statement is safe for python environment)
            # print(f"[AI Speed] Latency: {latency_ms:.1f}ms, Pred: {pred:.2f}m/s")
            
            return float(pred), confidence
            
        except Exception as e:
            print(f"AI Speed Inference error: {e}")
            return None, 0.0

    def fallback_speed(self, accel_window: np.ndarray, dt: float, prev_speed: float) -> float:
        """
        Simple kinematic integration fallback if AI is unavailable.
        """
        if len(accel_window) == 0:
            return prev_speed
            
        mean_forward_accel = np.mean(accel_window[:, 0])
        new_speed = prev_speed + (mean_forward_accel * dt)
        return max(0.0, new_speed)
