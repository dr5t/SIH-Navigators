import unittest
import numpy as np
from ml.datasets.io_vnbd import ImuData, GnssData
from navigation_core.filtering.synchronization import synchronize_imu, align_gnss_to_imu
from replay.gnss_blackout import inject_gnss_blackout

class TestPhase1(unittest.TestCase):
    def setUp(self):
        # Create mock IMU data (10 Hz for easy math)
        self.imu = ImuData(
            timestamp=np.arange(0, 10, 0.1),
            accel=np.ones((100, 3)),
            gyro=np.ones((100, 3)),
            mag=None
        )
        
        # Create mock GNSS data (1 Hz)
        self.gnss = GnssData(
            timestamp=np.arange(0, 10, 1.0),
            lat=np.ones(10) * 12.0,
            lon=np.ones(10) * 77.0,
            alt=np.ones(10) * 900.0,
            speed=np.ones(10) * 15.0,
            bearing=np.ones(10) * 90.0,
            accuracy=np.ones(10) * 5.0
        )

    def test_synchronization(self):
        # Resample IMU to 100 Hz
        resampled_imu = synchronize_imu(self.imu, target_freq_hz=100.0)
        self.assertEqual(len(resampled_imu.timestamp), 990)
        self.assertAlmostEqual(resampled_imu.timestamp[1] - resampled_imu.timestamp[0], 0.01)
        
        # Align GNSS to IMU
        aligned_gnss = align_gnss_to_imu(self.gnss, resampled_imu.timestamp)
        self.assertEqual(len(aligned_gnss.timestamp), 990)
        # Should carry forward the speed values using zero-order hold
        self.assertEqual(aligned_gnss.speed[0], 15.0)

    def test_gnss_blackout(self):
        # Inject a 3 second blackout from t=3 to t=6
        available, ground_truth = inject_gnss_blackout(self.gnss, start_time=3.0, duration=3.0)
        
        # GNSS at t=3, 4, 5, 6 should be in ground_truth (4 points)
        self.assertEqual(len(ground_truth.timestamp), 4)
        # Remaining 6 points should be in available
        self.assertEqual(len(available.timestamp), 6)
        
        self.assertNotIn(4.0, available.timestamp)
        self.assertIn(4.0, ground_truth.timestamp)

if __name__ == '__main__':
    unittest.main()
