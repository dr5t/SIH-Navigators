from abc import ABC, abstractmethod
from typing import List, Callable, Optional
from navigation_core.sensors.types import IMUMeasurement, GNSSMeasurement, SensorSource

class SensorProvider(ABC):
    def __init__(self, source: SensorSource):
        self.source = source
        self.imu_callbacks: List[Callable[[IMUMeasurement], None]] = []
        self.gnss_callbacks: List[Callable[[GNSSMeasurement], None]] = []
        self.is_running = False

    def register_imu_callback(self, cb: Callable[[IMUMeasurement], None]):
        self.imu_callbacks.append(cb)

    def register_gnss_callback(self, cb: Callable[[GNSSMeasurement], None]):
        self.gnss_callbacks.append(cb)

    def _notify_imu(self, measurement: IMUMeasurement):
        for cb in self.imu_callbacks:
            cb(measurement)

    def _notify_gnss(self, measurement: GNSSMeasurement):
        for cb in self.gnss_callbacks:
            cb(measurement)

    @abstractmethod
    def start(self):
        """Start acquiring data."""
        pass

    @abstractmethod
    def stop(self):
        """Stop acquiring data."""
        pass

class AndroidSensorProvider(SensorProvider):
    def __init__(self):
        super().__init__(SensorSource.LIVE_ANDROID)
        # Note: Actual android bindings (e.g. via chaquopy) will pump data into this provider
        
    def start(self):
        self.is_running = True
        
    def stop(self):
        self.is_running = False

class WebSensorProvider(SensorProvider):
    def __init__(self):
        super().__init__(SensorSource.LIVE_WEB)
        
    def start(self):
        self.is_running = True
        
    def stop(self):
        self.is_running = False

class ExternalIMUProvider(SensorProvider):
    def __init__(self, connection_string: str):
        super().__init__(SensorSource.EXTERNAL)
        self.connection_string = connection_string
        
    def start(self):
        self.is_running = True
        
    def stop(self):
        self.is_running = False

class ReplaySensorProvider(SensorProvider):
    def __init__(self, log_path: str):
        super().__init__(SensorSource.REPLAY)
        self.log_path = log_path
        
    def start(self):
        self.is_running = True
        # In a real implementation, this would start a thread that reads the log file
        # and calls _notify_imu and _notify_gnss at the correct simulated time.
        
    def stop(self):
        self.is_running = False
