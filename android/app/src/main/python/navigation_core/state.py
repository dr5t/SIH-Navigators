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

    def get_confidence_explanation(self) -> dict:
        confidence = "HIGH"
        reasons = []
        mitigations = []
        actions = []

        mode_name = self.mode.name
        if mode_name in ["GNSS_DEGRADED", "DEAD_RECKONING_DEGRADED"]:
            confidence = "LOW"
        elif mode_name in ["DEAD_RECKONING", "GNSS_REJECTED", "INITIALIZING"]:
            confidence = "MEDIUM"

        if getattr(self, "pos_uncertainty", 0) > 20:
            confidence = "LOW"

        # Determine reasons based on actual state
        if "DEAD_RECKONING" in mode_name or mode_name == "GNSS_REJECTED":
            reasons.append("GNSS unavailable or rejected")
            if getattr(self, "speed_source", "") == "AI":
                mitigations.append("AI speed active")
            elif getattr(self, "speed_source", "") == "KINEMATIC":
                mitigations.append("Vehicle constraints active")
        elif mode_name == "GNSS_DEGRADED":
            reasons.append("GNSS degraded")

        pos_unc = getattr(self, "pos_uncertainty", 0)
        if pos_unc > 15:
            reasons.append(f"Position uncertainty increased to {int(pos_unc)} m")

        map_status = getattr(self, "map_status", "UNKNOWN")
        if map_status != "MATCHED" and "GNSS" not in mode_name:
            reasons.append("Offline map matching unavailable")
        elif map_status == "MATCHED":
            mitigations.append("Offline map matching active")

        # Define actions based on state
        if confidence == "LOW" or confidence == "MEDIUM":
            actions.append("Run Diagnostics")
            if "GNSS" not in mode_name:
                actions.append("Check GNSS")
            if pos_unc > 25:
                actions.append("Recalibrate")

        # Cleanup if no specific reasons found but confidence is somehow dropped
        if confidence != "HIGH" and not reasons:
            reasons.append("Temporary state transition")

        return {
            "confidence": confidence,
            "reasons": reasons,
            "mitigations": mitigations,
            "actions": actions
        }
