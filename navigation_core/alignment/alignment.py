import numpy as np
from scipy.spatial.transform import Rotation
from navigation_core.ins.quaternion import Quaternion

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
    # Average gravity vector in body frame
    f_b = np.mean(accel_window, axis=0)
    
    # Normalize
    f_b_norm = np.linalg.norm(f_b)
    if f_b_norm < 1e-5:
        return Quaternion()
        
    f_b_hat = f_b / f_b_norm
    
    # In stationary conditions, specific force is opposite to gravity
    # Assuming ENU frame where gravity points down [0, 0, -g], specific force should be [0, 0, g]
    # So the unit vector in nav frame is [0, 0, 1]
    
    # Pitch and roll calculation
    # f_b = R_nav2body * [0, 0, 1]^T
    # Which means f_bx = -sin(pitch), f_by = sin(roll)cos(pitch), f_bz = cos(roll)cos(pitch)
    pitch = np.arcsin(-f_b_hat[0])
    roll = np.arctan2(f_b_hat[1], f_b_hat[2])
    yaw = np.radians(yaw_deg)
    
    # Scipy uses intrinsic rotations
    # ZYX corresponds to Yaw, Pitch, Roll
    rot = Rotation.from_euler('zyx', [yaw, pitch, roll])
    
    # Scipy quaternion is [x, y, z, w], we want [w, x, y, z]
    q = rot.as_quat()
    return Quaternion([q[3], q[0], q[1], q[2]])
