from dataclasses import dataclass
from typing import Optional
from navigation_core.fusion.state_machine import NavigationMode

@dataclass
class NavigationState:
    timestamp: float
    
    # Position
    latitude: float
    longitude: float
    altitude: float
    
    # Velocity (ENU)
    velocity_east: float
    velocity_north: float
    velocity_up: float
    
    # Attitude (Euler angles in radians)
    roll: float
    pitch: float
    yaw: float
    
    # Status
    mode: NavigationMode
    
    # Uncertainty (1-sigma)
    pos_uncertainty: float
    vel_uncertainty: float
    
    # Metadata
    speed_source: str = "GNSS" # "GNSS", "AI", "KINEMATIC"
    
    @property
    def speed_m_s(self) -> float:
        import math
        return math.sqrt(self.velocity_east**2 + self.velocity_north**2 + self.velocity_up**2)
