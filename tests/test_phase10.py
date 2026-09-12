import unittest
import numpy as np
from edge.engine import EdgeEngine

class TestPhase10(unittest.TestCase):
    def test_edge_engine_orchestration(self):
        engine = EdgeEngine(37.7, -122.4, 10.0)
        
        # Feed 60 samples of stationary IMU data
        accel = np.array([0.0, 0.0, 9.81])
        gyro = np.array([0.0, 0.0, 0.0])
        dt = 0.01
        
        for i in range(60):
            engine.process_imu(accel, gyro, dt, i * dt)
            
        # Verify ZUPT triggered and velocity is near zero
        self.assertEqual(len(engine.trajectory), 60)
        np.testing.assert_almost_equal(engine.trajectory[-1]['vel'], [0, 0, 0], decimal=2)
        
    def test_map_matching_integration(self):
        segments = np.array([
            [[0.0, 0.0], [10.0, 0.0]]
        ])
        engine = EdgeEngine(37.7, -122.4, 10.0, road_segments=segments)
        
        # Override pos to be slightly off the road
        engine.fusion.eskf.ins.pos = np.array([5.0, 2.0, 0.0])
        
        # Process 1 IMU step
        engine.process_imu(np.array([0.0, 0.0, 9.81]), np.zeros(3), 0.01, 1.0)
        
        # Should snap to [5.0, 0.0, 0.0]
        np.testing.assert_almost_equal(engine.trajectory[-1]['pos'][0:2], [5.0, 0.0])

if __name__ == '__main__':
    unittest.main()
