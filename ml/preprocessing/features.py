import numpy as np
from typing import Tuple

class FeatureExtractor:
    """
    Extracts fixed-length temporal windows from continuous IMU data.
    Ensures EXACT parity between training loops and Android inference.
    """
    def __init__(self, seq_len: int = 200, stride: int = 50, channels: int = 6):
        self.seq_len = seq_len
        self.stride = stride
        self.channels = channels
        
        # Hardcoded normalization parameters (in a real pipeline these would be learned and exported)
        self.accel_mean = np.array([0.0, 0.0, 9.8])
        self.accel_std = np.array([2.0, 2.0, 2.0])
        self.gyro_mean = np.array([0.0, 0.0, 0.0])
        self.gyro_std = np.array([0.5, 0.5, 0.5])

    def normalize(self, imu_data: np.ndarray) -> np.ndarray:
        """
        Normalizes IMU data (N, Channels).
        Channels: ax, ay, az, gx, gy, gz
        """
        norm_data = np.copy(imu_data)
        
        # Normalize Accel
        norm_data[:, 0:3] = (norm_data[:, 0:3] - self.accel_mean) / self.accel_std
        
        # Normalize Gyro
        norm_data[:, 3:6] = (norm_data[:, 3:6] - self.gyro_mean) / self.gyro_std
        
        return norm_data

    def create_windows(self, imu_data: np.ndarray, speed_data: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Creates overlapping windows.
        Avoids future-data leakage by taking the target speed at the END of the window.
        
        Returns:
            X: (num_windows, seq_len, channels) - Note PyTorch uses (N, C, L), so we might transpose later.
            y: (num_windows,) or None
        """
        norm_imu = self.normalize(imu_data)
        
        num_samples = len(norm_imu)
        if num_samples < self.seq_len:
            return np.empty((0, self.seq_len, self.channels)), np.empty(0)
            
        num_windows = (num_samples - self.seq_len) // self.stride + 1
        
        X = np.zeros((num_windows, self.seq_len, self.channels))
        y = np.zeros(num_windows) if speed_data is not None else None
        
        for i in range(num_windows):
            start = i * self.stride
            end = start + self.seq_len
            X[i] = norm_imu[start:end, :self.channels]
            
            if y is not None:
                # Target is the speed at the very end of the temporal window
                y[i] = speed_data[end - 1]
                
        # Transpose for PyTorch Conv1D: (Batch, SeqLen, Channels) -> (Batch, Channels, SeqLen)
        X = np.transpose(X, (0, 2, 1))
        
        return X, y
