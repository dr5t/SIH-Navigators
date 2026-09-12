import numpy as np
from navigation_core.fusion.eskf import ErrorStateEKF
from navigation_core.ins.coordinates import lla_to_enu
from navigation_core.alignment.alignment import compute_static_alignment

class GNSSFusionEngine:
    def __init__(self, ref_lat, ref_lon, ref_alt, initial_accel_window=None, initial_yaw=0.0):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.ref_alt = ref_alt
        
        # Initialize alignment if accel window is provided
        q_init = None
        if initial_accel_window is not None:
            q_init = compute_static_alignment(initial_accel_window, initial_yaw)
            
        self.eskf = ErrorStateEKF(initial_q=q_init) if q_init else ErrorStateEKF()
        
    def process_imu(self, accel: np.ndarray, gyro: np.ndarray, dt: float):
        """Processes a single IMU measurement."""
        self.eskf.predict(accel, gyro, dt)
        
    def process_gnss(self, lat: float, lon: float, alt: float, vn: float, ve: float, vd: float, pos_std: float, vel_std: float):
        """Processes a single GNSS measurement."""
        # Convert LLA to local ENU
        pos_enu = lla_to_enu(lat, lon, alt, self.ref_lat, self.ref_lon, self.ref_alt)
        
        # Velocity in ENU (assuming vn, ve, vd are provided in NED, we convert to ENU)
        # ENU = [East, North, Up]
        # NED = [North, East, Down]
        vel_enu = np.array([ve, vn, -vd])
        
        # Measurement Covariance Matrix R
        R_meas = np.zeros((6, 6))
        R_meas[0:3, 0:3] = np.eye(3) * (pos_std ** 2)
        R_meas[3:6, 3:6] = np.eye(3) * (vel_std ** 2)
        
        # Update ESKF
        self.eskf.update_gnss(pos_enu, vel_enu, R_meas)
        
    def get_state(self):
        """Returns current position, velocity, and orientation."""
        return {
            'pos': self.eskf.ins.pos.copy(),
            'vel': self.eskf.ins.vel.copy(),
            'q': self.eskf.ins.q.q.copy()
        }
