import numpy as np

def is_stationary(accel_window: np.ndarray, gyro_window: np.ndarray, 
                  accel_var_th: float = 0.05, gyro_var_th: float = 0.005) -> bool:
    """
    Detects if the vehicle is stationary based on IMU variance.
    """
    if len(accel_window) < 2 or len(gyro_window) < 2:
        return False
        
    accel_var = np.var(np.linalg.norm(accel_window, axis=1))
    gyro_var = np.var(np.linalg.norm(gyro_window, axis=1))
    
    return accel_var < accel_var_th and gyro_var < gyro_var_th

def apply_nhc(eskf, R_nhc: float = 1e-2):
    """
    Applies Non-Holonomic Constraints (lateral & vertical velocity = 0 in body frame)
    Updates the ESKF if significant lateral/vertical motion is found.
    """
    # R is Nav to Body inverse -> Body to Nav. Transpose is Nav to Body.
    R_b2n = eskf.ins.q.to_matrix()
    R_n2b = R_b2n.T
    
    # Velocity in body frame
    vel_body = R_n2b @ eskf.ins.vel
    
    # Measurement (vy_body = 0, vz_body = 0)
    z = np.array([0.0 - vel_body[1], 0.0 - vel_body[2]])
    
    # H matrix (2x15) maps state error (15) to measurement error (2).
    # We only observe velocity error (idx 3:6). 
    # v_body = R_n2b @ v_nav => H_vel = R_n2b. 
    # Since we only use Y and Z, we take the 2nd and 3rd rows of R_n2b.
    H = np.zeros((2, 15))
    H[0:2, 3:6] = R_n2b[1:3, :]
    
    # Measurement noise
    R = np.eye(2) * R_nhc
    
    # Kalman update
    S = H @ eskf.P @ H.T + R
    K = eskf.P @ H.T @ np.linalg.inv(S)
    
    dx = K @ z
    eskf._inject_error(dx)
    
    I = np.eye(15)
    eskf.P = (I - K @ H) @ eskf.P @ (I - K @ H).T + K @ R @ K.T

def apply_zupt(eskf, R_zupt: float = 1e-4):
    """
    Zero Velocity Update (ZUPT). Call when is_stationary() is True.
    """
    z = -eskf.ins.vel
    H = np.zeros((3, 15))
    H[0:3, 3:6] = np.eye(3)
    
    R = np.eye(3) * R_zupt
    
    S = H @ eskf.P @ H.T + R
    K = eskf.P @ H.T @ np.linalg.inv(S)
    
    dx = K @ z
    eskf._inject_error(dx)
    
    I = np.eye(15)
    eskf.P = (I - K @ H) @ eskf.P @ (I - K @ H).T + K @ R @ K.T
