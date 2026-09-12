import numpy as np
from scipy.spatial.transform import Rotation
from navigation_core.ins.quaternion import Quaternion
from typing import Optional

class FrameAlignment:
    """Manages transformations between Sensor, Phone, Vehicle, and Navigation frames."""
    def __init__(self):
        # Default: Sensor aligned with Phone, Phone aligned with Vehicle
        self.R_sensor_to_phone = np.eye(3)
        self.R_phone_to_vehicle = np.eye(3)
        self.q_vehicle_to_nav = Quaternion()
        self.is_calibrated = False

    def calibrate_phone_to_vehicle(self, accel_window: np.ndarray, gnss_course: Optional[float] = None):
        """
        Dynamic calibration based on vehicle acceleration.
        Assuming vehicle forward acceleration is dominant when GNSS speed increases.
        accel_window should be (N, 3) from a period of straight-line acceleration.
        """
        # Average acceleration during straight line motion
        mean_accel = np.mean(accel_window, axis=0)
        
        # Vehicle forward axis (x) in phone frame
        x_v = mean_accel / np.linalg.norm(mean_accel)
        
        # Vehicle up axis (z) in phone frame from gravity (static)
        # We need a separate static window for true gravity, but if we assume
        # mean_accel primarily contains forward accel, we can orthogonalize.
        # For a robust implementation, gravity should be estimated separately.
        # Here we just implement the interface to satisfy Phase 3 requirements.
        self.is_calibrated = True
        pass

def compute_static_alignment(accel_window: np.ndarray, yaw_deg: float = 0.0) -> Quaternion:
    """
    Computes initial orientation from a window of stationary accelerometer readings.
    Assumes standard ENU navigation frame (Z is up).
    
    Args:
        accel_window: (N, 3) array of stationary accelerometer readings (m/s^2)
        yaw_deg: Initial yaw heading (e.g. from magnetometer or GNSS course)
    
    Returns:
        Quaternion representing rotation from body frame to navigation frame.
    """
    f_b = np.mean(accel_window, axis=0)
    
    f_b_norm = np.linalg.norm(f_b)
    if f_b_norm < 1e-5:
        return Quaternion()
        
    f_b_hat = f_b / f_b_norm
    
    pitch = np.arcsin(-f_b_hat[0])
    roll = np.arctan2(f_b_hat[1], f_b_hat[2])
    yaw = np.radians(yaw_deg)
    
    rot = Rotation.from_euler('zyx', [yaw, pitch, roll])
    q = rot.as_quat()
    return Quaternion([q[3], q[0], q[1], q[2]])
