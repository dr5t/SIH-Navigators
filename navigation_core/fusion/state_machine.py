from enum import Enum, auto
from navigation_core.sensors.types import GNSSMeasurement, GNSSQuality

class NavigationMode(Enum):
    INITIALIZING = auto()
    GNSS_GOOD = auto()
    GNSS_DEGRADED = auto()
    GNSS_REJECTED = auto()
    DEAD_RECKONING = auto()
    DEAD_RECKONING_DEGRADED = auto()
    
class NavigationStateMachine:
    def __init__(self):
        self.mode = NavigationMode.INITIALIZING
        self.last_gnss_time = 0.0
        self.dr_start_time = 0.0
        self.consecutive_good_gnss = 0
        
    def process_gnss(self, gnss: GNSSMeasurement, current_time: float, current_state: 'NavigationState' = None, rejected_by_filter: bool = False) -> NavigationMode:
        """Evaluates GNSS measurement and updates the state machine."""
        
        if rejected_by_filter:
            self.mode = NavigationMode.GNSS_REJECTED
            self.consecutive_good_gnss = 0
            # If we were in DR, we remain essentially in DR, but we mark it as GNSS_REJECTED
            # Alternatively, if we reject, we can just treat it as an outage.
            self._enter_dr(current_time)
            return self.mode
            
        # GNSS Recovery Validation
        if self.mode in [NavigationMode.DEAD_RECKONING, NavigationMode.DEAD_RECKONING_DEGRADED, NavigationMode.GNSS_REJECTED] and current_state:
            # If GNSS comes back, check if it's wildly inconsistent with our map-matched state
            if gnss.quality != GNSSQuality.GOOD and current_state.map_status == "COVERAGE_GOOD":
                if current_state.map_match_confidence > 0.8:
                    # Ignore GNSS until we get a high-quality fix
                    self.mode = NavigationMode.GNSS_REJECTED
                    self.consecutive_good_gnss = 0
                    self._enter_dr(current_time)
                    return self.mode
                    
            # Require 3 consecutive good GNSS updates to recover from a long DR session to avoid initial jumps
            time_in_dr = current_time - self.dr_start_time
            if time_in_dr > 10.0 and gnss.quality == GNSSQuality.GOOD:
                if self.consecutive_good_gnss < 2:
                    self.consecutive_good_gnss += 1
                    # Still treat as rejected/DR until we have consistency
                    self.mode = NavigationMode.GNSS_REJECTED
                    self._enter_dr(current_time)
                    return self.mode
                    
        self.last_gnss_time = current_time
        self.consecutive_good_gnss += 1
        
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
