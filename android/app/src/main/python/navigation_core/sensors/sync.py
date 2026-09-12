from typing import Optional, Dict
from navigation_core.sensors.types import IMUMeasurement, GNSSMeasurement, SensorType, SensorHealth
import time

class SensorSynchronizer:
    def __init__(self, max_delay_ms: float = 50.0):
        self.max_delay_ms = max_delay_ms
        self.last_timestamps: Dict[SensorType, float] = {}
        self.last_gnss_time: Optional[float] = None
        self.start_time = time.time()
        
    def check_health(self, measurement: IMUMeasurement) -> SensorHealth:
        """Evaluates IMU health based on timestamps and saturation."""
        current_time = measurement.timestamp
        last_time = self.last_timestamps.get(measurement.sensor_type)
        
        health = SensorHealth.OPTIMAL
        
        if last_time is not None:
            dt = current_time - last_time
            if dt <= 0:
                health = SensorHealth.INVALID # Duplicate or out-of-order
            elif dt > self.max_delay_ms / 1000.0:
                health = SensorHealth.STALE
                
        # Check saturation (assuming typical smartphone limits, e.g., 4g for accel, 2000dps for gyro)
        if measurement.sensor_type == SensorType.ACCELEROMETER:
            if abs(measurement.x) > 39.2 or abs(measurement.y) > 39.2 or abs(measurement.z) > 39.2:
                health = SensorHealth.SATURATED
                
        self.last_timestamps[measurement.sensor_type] = current_time
        return health

    def sync_gnss(self, gnss: GNSSMeasurement) -> SensorHealth:
        """Evaluates GNSS health based on timestamps."""
        current_time = gnss.timestamp
        health = SensorHealth.OPTIMAL
        
        if self.last_gnss_time is not None:
            dt = current_time - self.last_gnss_time
            if dt <= 0:
                health = SensorHealth.INVALID
            elif dt > 2.0: # GNSS usually 1Hz, flag stale if > 2s
                health = SensorHealth.STALE
                
        self.last_gnss_time = current_time
        return health
