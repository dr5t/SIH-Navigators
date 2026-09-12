import time
from typing import Callable, Any

class ReplayEngine:
    """
    Basic replay engine that steps through synchronized IMU and GNSS data
    as if it were live.
    """
    def __init__(self, imu_data, gnss_data, nav_callback: Callable[[Any, Any], None]):
        self.imu = imu_data
        self.gnss = gnss_data
        self.nav_callback = nav_callback
        self.current_idx = 0
        self.is_playing = False
        
    def play(self, speed: float = 1.0):
        self.is_playing = True
        n_samples = len(self.imu.timestamp)
        
        while self.is_playing and self.current_idx < n_samples:
            # Simulate reading IMU
            imu_sample = {
                'timestamp': self.imu.timestamp[self.current_idx],
                'accel': self.imu.accel[self.current_idx],
                'gyro': self.imu.gyro[self.current_idx],
                'mag': self.imu.mag[self.current_idx] if self.imu.mag is not None else None
            }
            
            # Find matching GNSS (assuming aligned or lower frequency)
            # For simplicity, we just pass the GNSS data array and current time
            # The callback can handle filtering
            
            # Call navigation loop
            self.nav_callback(imu_sample, self.gnss)
            
            self.current_idx += 1
            
            if speed > 0 and self.current_idx < n_samples:
                dt = self.imu.timestamp[self.current_idx] - self.imu.timestamp[self.current_idx - 1]
                time.sleep(dt / speed)
                
    def pause(self):
        self.is_playing = False
        
    def reset(self):
        self.current_idx = 0
        self.is_playing = False
