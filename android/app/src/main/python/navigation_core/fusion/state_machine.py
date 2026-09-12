from enum import Enum, auto
from navigation_core.sensors.types import GNSSMeasurement, GNSSQuality

class NavigationMode(Enum):
    INITIALIZING = auto()
    GNSS_GOOD = auto()
    GNSS_DEGRADED = auto()
    DEAD_RECKONING = auto()
    DEAD_RECKONING_DEGRADED = auto()
    
class NavigationStateMachine:
    def __init__(self):
        self.mode = NavigationMode.INITIALIZING
        self.last_gnss_time = 0.0
        self.dr_start_time = 0.0
        
    def process_gnss(self, gnss: GNSSMeasurement, current_time: float) -> NavigationMode:
        """Evaluates GNSS measurement and updates the state machine."""
        self.last_gnss_time = current_time
        
        if gnss.quality == GNSSQuality.GOOD:
            self.mode = NavigationMode.GNSS_GOOD
        elif gnss.quality == GNSSQuality.DEGRADED:
            self.mode = NavigationMode.GNSS_DEGRADED
        else:
            # If poor or invalid, we treat it as an outage
            self._enter_dr(current_time)
            
        return self.mode
        
    def process_imu(self, current_time: float) -> NavigationMode:
        """Called on every IMU tick to check for GNSS timeouts."""
        # If we haven't received GNSS for > 2 seconds, enter DR
        time_since_gnss = current_time - self.last_gnss_time
        
        if self.mode in [NavigationMode.GNSS_GOOD, NavigationMode.GNSS_DEGRADED, NavigationMode.INITIALIZING]:
            if time_since_gnss > 2.0:
                self._enter_dr(current_time)
                
        elif self.mode in [NavigationMode.DEAD_RECKONING, NavigationMode.DEAD_RECKONING_DEGRADED]:
            dr_duration = current_time - self.dr_start_time
            if dr_duration > 60.0:
                # After 60 seconds of DR, accuracy is likely very poor
                self.mode = NavigationMode.DEAD_RECKONING_DEGRADED
                
        return self.mode
        
    def _enter_dr(self, current_time: float):
        if self.mode not in [NavigationMode.DEAD_RECKONING, NavigationMode.DEAD_RECKONING_DEGRADED]:
            self.mode = NavigationMode.DEAD_RECKONING
            self.dr_start_time = current_time
