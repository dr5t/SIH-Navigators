import numpy as np

class ExternalImuCalibration:
    def __init__(self):
        # Default identity alignment (assumes external IMU is mounted perfectly aligned with the vehicle)
        self.alignment_matrix = np.eye(3)
        self.gyro_bias = np.zeros(3)
        self.accel_bias = np.zeros(3)
        self.accel_scale_factor = np.eye(3)

    def set_alignment(self, roll_deg: float, pitch_deg: float, yaw_deg: float):
        """Sets the alignment matrix from Euler angles (extrinsic rotation)."""
        r = np.radians(roll_deg)
        p = np.radians(pitch_deg)
        y = np.radians(yaw_deg)
        
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(r), -np.sin(r)],
            [0, np.sin(r), np.cos(r)]
        ])
        Ry = np.array([
            [np.cos(p), 0, np.sin(p)],
            [0, 1, 0],
            [-np.sin(p), 0, np.cos(p)]
        ])
        Rz = np.array([
            [np.cos(y), -np.sin(y), 0],
            [np.sin(y), np.cos(y), 0],
            [0, 0, 1]
        ])
        self.alignment_matrix = Rz @ Ry @ Rx

    def apply(self, accel: np.ndarray, gyro: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Applies calibration and alignment to the raw sensor readings."""
        # 1. Remove bias and apply scale factor
        accel_calibrated = self.accel_scale_factor @ (accel - self.accel_bias)
        gyro_calibrated = gyro - self.gyro_bias
        
        # 2. Rotate to vehicle frame
        accel_aligned = self.alignment_matrix @ accel_calibrated
        gyro_aligned = self.alignment_matrix @ gyro_calibrated
        
        return accel_aligned, gyro_aligned
