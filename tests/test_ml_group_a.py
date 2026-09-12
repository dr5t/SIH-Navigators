import unittest
import numpy as np
from ml.preprocessing.sync import synchronize_sensors
from ml.datasets.io_vnbd import ImuData, GnssData
from ml.preprocessing.features import FeatureExtractor
from ml.datasets.split import split_sessions
from ml.models.baseline import KinematicBaseline

class TestMLGroupA(unittest.TestCase):

    def test_sync(self):
        # 1Hz GNSS
        gnss_t = np.array([0.0, 1.0, 2.0])
        gnss_s = np.array([5.0, 10.0, 15.0])
        gnss = GnssData(gnss_t, np.zeros(3), np.zeros(3), np.zeros(3), gnss_s, np.zeros(3), np.zeros(3))
        
        # 10Hz IMU
        imu_t = np.linspace(0.0, 2.0, 21)
        imu_acc = np.ones((21, 3))
        imu_gyr = np.zeros((21, 3))
        imu = ImuData(imu_t, imu_acc, imu_gyr)
        
        # Sync to 100Hz
        t, s_imu, s_speed = synchronize_sensors(imu, gnss, target_hz=100.0)
        
        self.assertEqual(len(t), 200)
        self.assertEqual(s_imu.shape, (200, 6))
        self.assertAlmostEqual(s_speed[100], 10.0, places=1) # at 1.0s, speed should be 10.0

    def test_feature_extraction(self):
        fe = FeatureExtractor(seq_len=50, stride=25, channels=6)
        
        imu_data = np.zeros((200, 6))
        speed_data = np.ones(200) * 15.0
        
        X, y = fe.create_windows(imu_data, speed_data)
        
        # 200 samples, len 50, stride 25 -> windows at [0:50], [25:75], [50:100], [75:125], [100:150], [125:175], [150:200]
        # (200 - 50) // 25 + 1 = 7 windows
        self.assertEqual(X.shape, (7, 6, 50))
        self.assertEqual(y.shape, (7,))
        self.assertEqual(y[0], 15.0)

    def test_session_split(self):
        sessions = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]
        train, val, test = split_sessions(sessions, 0.7, 0.15, seed=42)
        
        self.assertEqual(len(train), 7)
        self.assertTrue(len(val) in [1, 2])
        self.assertEqual(len(train) + len(val) + len(test), 10)
        
        # Ensure no overlap
        self.assertTrue(len(set(train) & set(val)) == 0)
        self.assertTrue(len(set(val) & set(test)) == 0)

    def test_baseline(self):
        baseline = KinematicBaseline(dt=0.01)
        # 1 window, 50 samples, 6 channels
        # If channel 0 is accel X = 1.0 m/s^2 for 50 samples (0.5s)
        X = np.zeros((1, 50, 6))
        X[0, :, 0] = 1.0
        
        pred = baseline.predict(X)
        self.assertAlmostEqual(pred[0], 0.5)

if __name__ == '__main__':
    unittest.main()
