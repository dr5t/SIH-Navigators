import unittest
import numpy as np
from navigation_core.fusion.eskf import ErrorStateEKF
from navigation_core.constraints.constraints import is_stationary, apply_nhc, apply_zupt

class TestPhase3(unittest.TestCase):
    def test_stationary_detection(self):
        # Create stationary window (low variance)
        accel = np.ones((50, 3)) * 9.81
        gyro = np.zeros((50, 3))
        
        # Add tiny noise
        accel += np.random.normal(0, 0.01, (50, 3))
        gyro += np.random.normal(0, 0.001, (50, 3))
        
        self.assertTrue(is_stationary(accel, gyro))
        
        # Create moving window (high variance)
        accel_moving = accel + np.random.normal(0, 2.0, (50, 3))
        self.assertFalse(is_stationary(accel_moving, gyro))

    def test_zupt(self):
        eskf = ErrorStateEKF()
        eskf.ins.vel = np.array([1.0, -0.5, 0.2])
        
        # Apply ZUPT multiple times to simulate convergence over time
        for _ in range(10):
            apply_zupt(eskf)
            
        # Velocity should be reduced significantly (by ~10x)
        np.testing.assert_array_less(np.abs(eskf.ins.vel), [0.15, 0.15, 0.15])
        
    def test_nhc(self):
        eskf = ErrorStateEKF()
        
        # Suppose body frame = nav frame (identity orientation)
        # Vehicle moving forward (X) but drifting right (Y) and down (Z)
        eskf.ins.vel = np.array([10.0, 2.0, -1.0])
        
        # Apply NHC multiple times to simulate convergence
        for _ in range(10):
            # Use small R_nhc to ensure it converges fast in the test
            apply_nhc(eskf, R_nhc=1e-4)
            
        # Forward velocity (X) should be mostly preserved
        self.assertGreater(eskf.ins.vel[0], 9.0)
        
        # Lateral (Y) and vertical (Z) velocity should be reduced
        np.testing.assert_array_less(np.abs(eskf.ins.vel[1:]), [0.5, 0.5])

if __name__ == '__main__':
    unittest.main()
