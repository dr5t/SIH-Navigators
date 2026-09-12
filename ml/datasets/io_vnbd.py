import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

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
    Assumes CSVs with standard columns. 
    Can be adjusted once exact schema is known.
    """
    def __init__(self, imu_path: str, gnss_path: str):
        self.imu_path = imu_path
        self.gnss_path = gnss_path

    def load_imu(self) -> ImuData:
        df = pd.read_csv(self.imu_path)
        # Expected cols: timestamp, ax, ay, az, gx, gy, gz, mx, my, mz
        # If mag is missing, we ignore it
        timestamp = df['timestamp'].values
        accel = df[['ax', 'ay', 'az']].values
        gyro = df[['gx', 'gy', 'gz']].values
        
        mag = None
        if all(c in df.columns for c in ['mx', 'my', 'mz']):
            mag = df[['mx', 'my', 'mz']].values
            
        return ImuData(timestamp=timestamp, accel=accel, gyro=gyro, mag=mag)
    
    def load_gnss(self) -> GnssData:
        df = pd.read_csv(self.gnss_path)
        # Expected cols: timestamp, lat, lon, alt, speed, bearing, accuracy
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
