from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class SensorType(Enum):
    ACCELEROMETER = auto()
    GYROSCOPE = auto()
    MAGNETOMETER = auto()
    GNSS = auto()
    EXTERNAL_IMU = auto()

class SensorSource(Enum):
    LIVE_ANDROID = auto()
    LIVE_WEB = auto()
    EXTERNAL = auto()
    REPLAY = auto()

class GNSSQuality(Enum):
    GOOD = auto()
    DEGRADED = auto()
    POOR = auto()
    INVALID = auto()
    LOST = auto()
    
class SensorHealth(Enum):
    OPTIMAL = auto()
    NOISY = auto()
    SATURATED = auto()
    STALE = auto()
    INVALID = auto()
    UNAVAILABLE = auto()

@dataclass
class IMUMeasurement:
    timestamp: float
    sensor_type: SensorType
    x: float
    y: float
    z: float
    accuracy: float
    source: SensorSource
    sequence_number: int
    health: SensorHealth = SensorHealth.OPTIMAL

@dataclass
class GNSSMeasurement:
    timestamp: float
    latitude: float
    longitude: float
    altitude: Optional[float]
    speed: Optional[float]
    course: Optional[float]
    horizontal_accuracy: Optional[float]
    vertical_accuracy: Optional[float]
    provider: str
    quality: GNSSQuality
    satellite_count: Optional[int]
    source: SensorSource
    sequence_number: int
    health: SensorHealth = SensorHealth.OPTIMAL
