import unittest
import numpy as np
from navigation_core.engine import NavigationEngine

class TestAIAblation(unittest.TestCase):
    
    def simulate_drive(self, enable_ai: bool):
        engine = NavigationEngine(37.7749, -122.4194, 10.0)
        
        if not enable_ai:
            engine.speed_estimator.is_available = False
            
        # Initialize GNSS
        engine.process_gnss(37.7749, -122.4194, 10.0, 5.0, 90.0, 1.0, 0.0)
        
        accel = np.array([5.0, 0.0, 9.8])
        gyro = np.array([0.0, 0.0, 0.0])
        
        # Drive offline (DR mode) for 50 steps
        last_state = None
        for i in range(1, 50):
            last_state = engine.process_imu(accel, gyro, 0.1, i * 0.1)
            
        return last_state
        
    def test_ablation(self):
        print("\n--- AI Ablation Navigation Test ---")
        
        state_no_ai = self.simulate_drive(enable_ai=False)
        speed_no_ai = state_no_ai["speed"]
        print(f"Final Speed (No AI - Kinematics Fallback): {speed_no_ai:.2f} m/s")
        
        state_ai = self.simulate_drive(enable_ai=True)
        speed_ai = state_ai["speed"]
        print(f"Final Speed (With AI): {speed_ai:.2f} m/s")
        
        # Verify GNSS independence - Both runs survived in DEAD_RECKONING
        self.assertEqual(state_no_ai["mode"], "DEAD_RECKONING")
        self.assertEqual(state_ai["mode"], "DEAD_RECKONING")
        
        self.assertIsNotNone(speed_ai)
        self.assertIsNotNone(speed_no_ai)

if __name__ == '__main__':
    unittest.main()
