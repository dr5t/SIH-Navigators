from dataclasses import dataclass
import numpy as np

@dataclass
class TrajectoryPoint:
    timestamp: float
    lat: float
    lon: float
    alt: float
    speed: float
    heading: float
    is_gnss: bool

class TrajectoryLoader:
    """
    Loads and manages ground-truth/reference trajectories.
    """
    def __init__(self, gnss_data):
        self.gnss = gnss_data
        
    def get_trajectory(self):
        trajectory = []
        for i in range(len(self.gnss.timestamp)):
            trajectory.append(TrajectoryPoint(
                timestamp=self.gnss.timestamp[i],
                lat=self.gnss.lat[i],
                lon=self.gnss.lon[i],
                alt=self.gnss.alt[i],
                speed=self.gnss.speed[i],
                heading=self.gnss.bearing[i],
                is_gnss=True
            ))
        return trajectory
