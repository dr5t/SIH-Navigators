import unittest
import numpy as np
from navigation_core.fusion.state_machine import NavigationStateMachine, NavigationMode
from navigation_core.sensors.types import GNSSMeasurement, GNSSQuality, SensorSource, SensorHealth
from navigation_core.fusion.eskf import ErrorStateEKF

class TestGroupC(unittest.TestCase):

    def test_state_machine_transitions(self):
        sm = NavigationStateMachine()
        self.assertEqual(sm.mode, NavigationMode.INITIALIZING)
        
        # Good GNSS
        gnss = GNSSMeasurement(10.0, 37.0, -122.0, 10.0, 15.0, 0.0, 1.0, 2.0, "gps", GNSSQuality.GOOD, 8, SensorSource.REPLAY, 1)
        mode = sm.process_gnss(gnss, 10.0)
        self.assertEqual(mode, NavigationMode.GNSS_GOOD)
        
        # 1.5 seconds later, IMU tick (should still be GOOD)
        mode = sm.process_imu(11.5)
        self.assertEqual(mode, NavigationMode.GNSS_GOOD)
        
        # 3.0 seconds later, IMU tick without GNSS (should trigger DR)
        mode = sm.process_imu(13.0)
        self.assertEqual(mode, NavigationMode.DEAD_RECKONING)
        
        # 75 seconds later, still no GNSS
        mode = sm.process_imu(85.0)
        self.assertEqual(mode, NavigationMode.DEAD_RECKONING_DEGRADED)
        
        # GNSS recovers
        gnss.timestamp = 86.0
        mode = sm.process_gnss(gnss, 86.0)
        self.assertEqual(mode, NavigationMode.GNSS_GOOD)

    def test_eskf_gating(self):
        eskf = ErrorStateEKF()
        
        # Provide a massive GNSS jump
        pos_jump = np.array([1000.0, 1000.0, 1000.0]) # 1000m jump
        vel = np.zeros(3)
        R_meas = np.eye(6)
        
        # Store original P trace
        tr_P_orig = np.trace(eskf.P)
        
        eskf.update_gnss(pos_jump, vel, R_meas)
        
        # If gating worked, it scaled R_meas up, so the kalman gain K was small,
        # meaning the injection dx was small relative to the massive 1000m jump.
        self.assertTrue(np.linalg.norm(eskf.ins.pos) < 500.0)
        
if __name__ == '__main__':
    unittest.main()
