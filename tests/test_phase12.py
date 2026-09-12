import unittest
import numpy as np
from benchmarking.metrics import calculate_rmse, evaluate_trajectory

class TestPhase12(unittest.TestCase):
    def test_rmse_calculation(self):
        est = np.array([[1.0, 2.0], [3.0, 4.0]])
        gt = np.array([[1.0, 2.0], [3.0, 4.0]])
        self.assertEqual(calculate_rmse(est, gt), 0.0)
        
        est2 = np.array([[0.0, 0.0]])
        gt2 = np.array([[3.0, 4.0]])
        # distance squared is 9 + 16 = 25. sqrt(25) = 5.0
        self.assertEqual(calculate_rmse(est2, gt2), 5.0)

    def test_evaluate_trajectory(self):
        est_traj = [
            {'pos': np.array([3.0, 4.0, 0.0]), 'vel': np.array([1.0, 0.0, 0.0])}
        ]
        gt_traj = [
            {'pos': np.array([0.0, 0.0, 0.0]), 'vel': np.array([0.0, 0.0, 0.0])}
        ]
        
        results = evaluate_trajectory(est_traj, gt_traj)
        self.assertEqual(results['pos_rmse'], 5.0)
        self.assertEqual(results['2d_pos_rmse'], 5.0)
        self.assertEqual(results['vel_rmse'], 1.0)

if __name__ == '__main__':
    unittest.main()
