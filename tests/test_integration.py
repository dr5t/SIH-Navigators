import unittest
import numpy as np
from navigation_core.engine import NavigationEngine
from navigation_core.fusion.state_machine import NavigationMode

class TestIntegration(unittest.TestCase):

    def test_full_pipeline(self):
        # 1. Initialize Engine
        engine = NavigationEngine(37.7749, -122.4194, 10.0)
        
        # 2. Feed it GNSS
        # lat, lon, alt, speed, course, h_acc, timestamp
        state1 = engine.process_gnss(37.7749, -122.4194, 10.0, 5.0, 90.0, 1.0, 0.0)
        self.assertEqual(state1["mode"], NavigationMode.GNSS_GOOD.name)
        
        # 3. Feed it IMU
        accel = np.array([5.0, 0.0, 9.8]) # Accelerating forward (East in ENU)
        gyro = np.array([0.0, 0.0, 0.0])
        
        for i in range(1, 10):
            state_imu = engine.process_imu(accel, gyro, 0.1, i * 0.1)
            
        self.assertEqual(state_imu["mode"], NavigationMode.GNSS_GOOD.name)
        
        # 4. Trigger GNSS Outage (Wait > 2 seconds)
        for i in range(10, 30):
            state_dr = engine.process_imu(accel, gyro, 0.1, i * 0.1)
            
        self.assertEqual(state_dr["mode"], NavigationMode.DEAD_RECKONING.name)
        
        # 5. Pipeline completed successfully without crashing
        self.assertIsNotNone(state_dr["speed"])

if __name__ == '__main__':
    unittest.main()
