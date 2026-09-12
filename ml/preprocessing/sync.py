import numpy as np
from scipy.interpolate import interp1d
from ml.datasets.io_vnbd import ImuData, GnssData
from typing import Tuple

def synchronize_sensors(imu: ImuData, gnss: GnssData, target_hz: float = 100.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Synchronizes IMU and GNSS data to a fixed frequency grid using linear interpolation.
    Note: Real-time inference does not use interpolation (it uses causal windows), 
    but for creating supervised training targets, interpolation aligns labels with inputs.
    
    Returns:
        synced_timestamps, synced_imu (N, 6 or 9), synced_speed (N,)
    """
    if len(imu.timestamp) < 2 or len(gnss.timestamp) < 2:
        raise ValueError("Insufficient data to synchronize.")
        
    # Define common time overlap
    start_time = max(imu.timestamp[0], gnss.timestamp[0])
    end_time = min(imu.timestamp[-1], gnss.timestamp[-1])
    
    if start_time >= end_time:
        raise ValueError("No overlapping time between IMU and GNSS.")
        
    dt = 1.0 / target_hz
    synced_timestamps = np.arange(start_time, end_time, dt)
    
    # Interpolate IMU
    imu_features = np.hstack((imu.accel, imu.gyro))
    if imu.mag is not None:
        imu_features = np.hstack((imu_features, imu.mag))
        
    f_imu = interp1d(imu.timestamp, imu_features, axis=0, bounds_error=False, fill_value="extrapolate")
    synced_imu = f_imu(synced_timestamps)
    
    # Interpolate GNSS Speed (Target)
    # Note: GNSS speed is typically delayed/smoothed, but for baseline training we align directly.
    f_gnss_speed = interp1d(gnss.timestamp, gnss.speed, bounds_error=False, fill_value="extrapolate")
    synced_speed = f_gnss_speed(synced_timestamps)
    
    return synced_timestamps, synced_imu, synced_speed
