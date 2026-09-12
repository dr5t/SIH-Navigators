import unittest
import numpy as np
from navigation_core.ai.speed_estimator import AISpeedEstimator
from navigation_core.constraints.vehicle import NonHolonomicConstraints
from navigation_core.ins.quaternion import Quaternion
from scipy.spatial.transform import Rotation

class TestGroupB(unittest.TestCase):

    def test_speed_estimator_fallback(self):
        estimator = AISpeedEstimator("dummy_path.pt")
        self.assertFalse(estimator.is_available)
        
        # Test kinematic fallback
        accel_window = np.array([
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0]
        ])
        
        speed = estimator.fallback_speed(accel_window, 0.1, 10.0)
        self.assertAlmostEqual(speed, 10.1)
        
    def test_non_holonomic_constraints(self):
        nhc = NonHolonomicConstraints()
        
        # Vehicle is aligned with ENU (yaw=0)
        q = Quaternion() 
        
        # Velocity in nav frame (forward=North, lateral=East)
        v_nav = np.array([1.0, 10.0, 0.5]) # Moving 10 m/s North (y-vehicle), but sliding East 1m/s, and climbing 0.5m/s
        
        # But wait, ENU is East, North, Up. If vehicle is aligned with ENU, 
        # Vehicle X = East
        # Vehicle Y = North
        # Vehicle Z = Up
        
        # In a typical ground vehicle frame:
        # X = Forward
        # Y = Left/Right (lateral)
        # Z = Up/Down
        
        # For this test, let's just see if it correctly penalizes non-zero Y and Z 
        # based on the R_n2v transform.
        innovation, H, R = nhc.generate_virtual_measurements(v_nav, q)
        
        # Measurement is [0, 0] for y, z
        # Prediction is [10.0, 0.5] if R_n2v is identity and we take idx 1 and 2
        self.assertAlmostEqual(innovation[0], -10.0)
        self.assertAlmostEqual(innovation[1], -0.5)
        
        self.assertEqual(H.shape, (2, 3))
        self.assertEqual(R.shape, (2, 2))

if __name__ == '__main__':
    unittest.main()
