import numpy as np
from navigation_core.ins.quaternion import Quaternion
from navigation_core.sensors.types import IMUMeasurement, SensorType

class AttitudeEstimator:
    """Estimates attitude (roll, pitch, yaw) fusing accel, gyro, and optionally mag."""
    
    def __init__(self, beta: float = 0.1):
        # Madgwick filter beta parameter
        self.beta = beta
        self.q = Quaternion()
        
    def update(self, gyro: np.ndarray, accel: np.ndarray, dt: float, mag: np.ndarray = None):
        """
        Madgwick or Mahony filter step.
        For simplicity, a basic complementary/Madgwick-style update.
        """
        # Gyro integration
        # q_dot = 0.5 * q * [0, gx, gy, gz]
        gx, gy, gz = gyro
        q_dot = np.array([
            -0.5 * (self.q.q[1]*gx + self.q.q[2]*gy + self.q.q[3]*gz),
             0.5 * (self.q.q[0]*gx - self.q.q[3]*gy + self.q.q[2]*gz),
             0.5 * (self.q.q[3]*gx + self.q.q[0]*gy - self.q.q[1]*gz),
             0.5 * (-self.q.q[2]*gx + self.q.q[1]*gy + self.q.q[0]*gz)
        ])
        
        # Accelerometer correction (simplified)
        norm_accel = np.linalg.norm(accel)
        if norm_accel > 0.1:
            ax, ay, az = accel / norm_accel
            
            # Gradient descent step based on gravity
            # F(q, a) = [ 2*(q1*q3 - q0*q2) - ax,
            #             2*(q0*q1 + q2*q3) - ay,
            #             2*(0.5 - q1**2 - q2**2) - az ]
            # J is the Jacobian of F. 
            # delta_f = J.T * F
            
            q0, q1, q2, q3 = self.q.q
            f = np.array([
                2*(q1*q3 - q0*q2) - ax,
                2*(q0*q1 + q2*q3) - ay,
                2*(0.5 - q1**2 - q2**2) - az
            ])
            
            J = np.array([
                [-2*q2,  2*q3, -2*q0,  2*q1],
                [ 2*q1,  2*q0,  2*q3,  2*q2],
                [    0, -4*q1, -4*q2,     0]
            ])
            
            step = J.T @ f
            norm_step = np.linalg.norm(step)
            if norm_step > 0:
                step /= norm_step
                
            q_dot -= self.beta * step
            
        # Optional: Magnetometer correction logic here if mag is present and undisturbed
        # ...
        
        # Integrate and normalize
        new_q = self.q.q + q_dot * dt
        self.q = Quaternion(new_q / np.linalg.norm(new_q))
        
    def get_euler_angles(self):
        """Returns roll, pitch, yaw in radians."""
        q0, q1, q2, q3 = self.q.q
        
        roll = np.arctan2(2 * (q0*q1 + q2*q3), 1 - 2*(q1**2 + q2**2))
        
        sinp = 2 * (q0*q2 - q3*q1)
        pitch = np.arcsin(np.clip(sinp, -1.0, 1.0))
        
        yaw = np.arctan2(2 * (q0*q3 + q1*q2), 1 - 2*(q2**2 + q3**2))
        
        return roll, pitch, yaw
