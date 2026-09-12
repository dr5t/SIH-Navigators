import numpy as np
from navigation_core.ins.quaternion import Quaternion

class INSPropagator:
    """
    Propagates navigation state (position, velocity, orientation) using 
    IMU data (specific force and angular rate).
    """
    def __init__(self, pos_enu=np.zeros(3), vel_enu=np.zeros(3), q=Quaternion()):
        self.pos = np.array(pos_enu, dtype=float)
        self.vel = np.array(vel_enu, dtype=float)
        self.q = q
        self.gravity = np.array([0.0, 0.0, -9.80665])  # Standard gravity in ENU
        
    def propagate(self, accel_body: np.ndarray, gyro_body: np.ndarray, dt: float):
        """
        Propagates state by one time step dt.
        
        Args:
            accel_body: (3,) specific force in body frame (m/s^2)
            gyro_body: (3,) angular rate in body frame (rad/s)
            dt: time step in seconds
        """
        # 1. Update orientation
        self.q.update(gyro_body, dt)
        
        # 2. Transform specific force to navigation frame
        R = self.q.to_matrix()
        accel_nav = R @ accel_body
        
        # 3. Compensate for gravity
        accel_nav = accel_nav + self.gravity
        
        # 4. Update velocity and position
        self.pos += self.vel * dt + 0.5 * accel_nav * dt * dt
        self.vel += accel_nav * dt
