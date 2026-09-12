import unittest
import numpy as np
from navigation_core.sensors.types import IMUMeasurement, SensorType, SensorSource, SensorHealth
from navigation_core.sensors.sync import SensorSynchronizer
from navigation_core.alignment.alignment import FrameAlignment, compute_static_alignment
from navigation_core.filtering.attitude import AttitudeEstimator

class TestGroupA(unittest.TestCase):

    def test_sensor_health_sync(self):
        sync = SensorSynchronizer(max_delay_ms=50.0)
        
        # Optimal reading
        m1 = IMUMeasurement(1.0, SensorType.ACCELEROMETER, 0.0, 0.0, 9.8, 1.0, SensorSource.REPLAY, 1)
        h1 = sync.check_health(m1)
        self.assertEqual(h1, SensorHealth.OPTIMAL)
        
        # Stale reading (> 50ms delay)
        m2 = IMUMeasurement(1.1, SensorType.ACCELEROMETER, 0.0, 0.0, 9.8, 1.0, SensorSource.REPLAY, 2)
        h2 = sync.check_health(m2)
        self.assertEqual(h2, SensorHealth.STALE)
        
        # Saturated reading (> 39.2)
        m3 = IMUMeasurement(1.12, SensorType.ACCELEROMETER, 40.0, 0.0, 9.8, 1.0, SensorSource.REPLAY, 3)
        h3 = sync.check_health(m3)
        self.assertEqual(h3, SensorHealth.SATURATED)

    def test_attitude_estimator(self):
        att = AttitudeEstimator(beta=0.1)
        
        # Simulate static device, z-up
        accel = np.array([0.0, 0.0, 9.8])
        gyro = np.array([0.0, 0.0, 0.0])
        
        for _ in range(100):
            att.update(gyro, accel, 0.01)
            
        r, p, y = att.get_euler_angles()
        
        self.assertAlmostEqual(r, 0.0, places=2)
        self.assertAlmostEqual(p, 0.0, places=2)
        self.assertAlmostEqual(y, 0.0, places=2)

if __name__ == '__main__':
    unittest.main()
