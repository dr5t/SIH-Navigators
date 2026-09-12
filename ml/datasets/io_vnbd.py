import os
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, List

@dataclass
class ImuData:
    timestamp: np.ndarray
    accel: np.ndarray  # (N, 3)
    gyro: np.ndarray   # (N, 3)
    mag: Optional[np.ndarray] = None # (N, 3)

@dataclass
class GnssData:
    timestamp: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    alt: np.ndarray
    speed: np.ndarray
    bearing: np.ndarray
    accuracy: np.ndarray

class IOVNBDParser:
    """
    Parses IO-VNBD dataset format.
    Validates CSVs for NaNs, missing timestamps, and monotonicity.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.imu_path = os.path.join(data_dir, "imu.csv")
        self.gnss_path = os.path.join(data_dir, "gnss.csv")

    def exists(self) -> bool:
        return os.path.exists(self.imu_path) and os.path.exists(self.gnss_path)

    def load_imu(self) -> ImuData:
        if not os.path.exists(self.imu_path):
            raise FileNotFoundError(f"Missing dataset file: {self.imu_path}")
            
        df = pd.read_csv(self.imu_path)
        
        # Validation
        if df['timestamp'].isnull().any():
            print(f"Warning: Dropping {df['timestamp'].isnull().sum()} IMU rows with missing timestamps.")
            df = df.dropna(subset=['timestamp'])
            
        df = df.sort_values(by='timestamp')
        
        timestamp = df['timestamp'].values
        accel = df[['ax', 'ay', 'az']].values
        gyro = df[['gx', 'gy', 'gz']].values
        
        mag = None
        if all(c in df.columns for c in ['mx', 'my', 'mz']):
            mag = df[['mx', 'my', 'mz']].values
            
        return ImuData(timestamp=timestamp, accel=accel, gyro=gyro, mag=mag)
    
    def load_gnss(self) -> GnssData:
        if not os.path.exists(self.gnss_path):
            raise FileNotFoundError(f"Missing dataset file: {self.gnss_path}")
            
        df = pd.read_csv(self.gnss_path)
        
        # Validation
        if df['timestamp'].isnull().any():
            print(f"Warning: Dropping {df['timestamp'].isnull().sum()} GNSS rows with missing timestamps.")
            df = df.dropna(subset=['timestamp'])
            
        if df['speed'].isnull().any():
            print(f"Warning: Dropping {df['speed'].isnull().sum()} GNSS rows with missing speed reference.")
            df = df.dropna(subset=['speed'])
            
        df = df.sort_values(by='timestamp')
        
        return GnssData(
            timestamp=df['timestamp'].values,
            lat=df['lat'].values,
            lon=df['lon'].values,
            alt=df['alt'].values,
            speed=df['speed'].values,
            bearing=df['bearing'].values,
            accuracy=df['accuracy'].values
        )

    def load_all(self) -> Tuple[ImuData, GnssData]:
        return self.load_imu(), self.load_gnss()

def list_sessions(base_dir: str = "ml/data/io_vnbd") -> List[str]:
    """Finds all valid IO-VNBD session directories."""
    if not os.path.exists(base_dir):
        return []
    
    sessions = []
    for item in os.listdir(base_dir):
        path = os.path.join(base_dir, item)
        if os.path.isdir(path):
            parser = IOVNBDParser(path)
            if parser.exists():
                sessions.append(path)
    return sorted(sessions)
