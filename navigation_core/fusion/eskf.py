import numpy as np
from navigation_core.ins.propagation import INSPropagator
from navigation_core.ins.quaternion import Quaternion

class ErrorStateEKF:
    """
    Error-State Extended Kalman Filter for GNSS+INS Fusion.
    State vector (15x1):
    - Position error (3)
    - Velocity error (3)
    - Attitude error (3)
    - Accelerometer bias error (3)
    - Gyroscope bias error (3)
    """
    def __init__(self, initial_pos=np.zeros(3), initial_vel=np.zeros(3), initial_q=Quaternion()):
        self.ins = INSPropagator(pos_enu=initial_pos, vel_enu=initial_vel, q=initial_q)
        
        self.accel_bias = np.zeros(3)
        self.gyro_bias = np.zeros(3)
        
        # 15x15 Error Covariance
        self.P = np.eye(15) * 1e-4
        # Increased uncertainty for biases
        self.P[9:15, 9:15] = np.eye(6) * 1e-2
        
        # Process noise covariance (Q)
        self.Q = np.eye(15) * 1e-5
        
    def predict(self, accel_meas: np.ndarray, gyro_meas: np.ndarray, dt: float):
        """
        Predict step: propagates the nominal state and the error covariance.
        """
        # Correct measurements with current biases
        accel_body = accel_meas - self.accel_bias
        gyro_body = gyro_meas - self.gyro_bias
        
        # Propagate nominal state
        R_prev = self.ins.q.to_matrix()
        self.ins.propagate(accel_body, gyro_body, dt)
        
        # Compute Jacobians for error state propagation
        F = np.eye(15)
        
        # Position error dot = Velocity error
        F[0:3, 3:6] = np.eye(3) * dt
        
        # Velocity error dot = -R * [f_body x] * attitude_error - R * accel_bias_error
        f_body = accel_body
        f_cross = np.array([
            [0, -f_body[2], f_body[1]],
            [f_body[2], 0, -f_body[0]],
            [-f_body[1], f_body[0], 0]
        ])
        F[3:6, 6:9] = -R_prev @ f_cross * dt
        F[3:6, 9:12] = -R_prev * dt
        
        # Attitude error dot = - [omega x] * attitude_error - gyro_bias_error
        omega = gyro_body
        omega_cross = np.array([
            [0, -omega[2], omega[1]],
            [omega[2], 0, -omega[0]],
            [-omega[1], omega[0], 0]
        ])
        F[6:9, 6:9] = np.eye(3) - omega_cross * dt
        F[6:9, 12:15] = -np.eye(3) * dt
        
        # Propagate Covariance
        self.P = F @ self.P @ F.T + self.Q * dt
        
    def update_gnss(self, gnss_pos: np.ndarray, gnss_vel: np.ndarray, R_meas: np.ndarray):
        """
        Update step using GNSS position and velocity.
        """
        # Measurement matrix H (6x15): observing pos and vel error
        H = np.zeros((6, 15))
        H[0:3, 0:3] = np.eye(3)
        H[3:6, 3:6] = np.eye(3)
        
        # Innovation
        z = np.zeros(6)
        z[0:3] = gnss_pos - self.ins.pos
        z[3:6] = gnss_vel - self.ins.vel
        
        # Kalman Gain
        S = H @ self.P @ H.T + R_meas
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # Compute Error State
        dx = K @ z
        
        # Update nominal state
        self._inject_error(dx)
        
        # Update Covariance
        I = np.eye(15)
        self.P = (I - K @ H) @ self.P @ (I - K @ H).T + K @ R_meas @ K.T
        
    def _inject_error(self, dx: np.ndarray):
        """
        Injects the error state back into the nominal state and resets error to 0.
        """
        # Pos and vel
        self.ins.pos += dx[0:3]
        self.ins.vel += dx[3:6]
        
        # Attitude error is a rotation vector.
        # Create a small rotation quaternion and multiply
        da = dx[6:9]
        theta = np.linalg.norm(da)
        if theta > 1e-8:
            s = np.sin(theta/2) / theta
            dq = np.array([np.cos(theta/2), da[0]*s, da[1]*s, da[2]*s])
        else:
            dq = np.array([1.0, da[0]/2, da[1]/2, da[2]/2])
            
        self.ins.q.q = self.ins.q._multiply(dq, self.ins.q.q)
        self.ins.q.normalize()
        
        # Biases
        self.accel_bias += dx[9:12]
        self.gyro_bias += dx[12:15]
