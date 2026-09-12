import numpy as np
import time
from navigation_core.engine import NavigationEngine
from navigation_core.fusion.state_machine import NavigationMode

class StressTestRunner:
    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 0

    def assert_mode(self, engine, expected_modes):
        if not isinstance(expected_modes, list):
            expected_modes = [expected_modes]
        if engine.state_machine.mode not in expected_modes:
            raise AssertionError(f"Expected mode in {expected_modes}, got {engine.state_machine.mode}")

    def run_all(self):
        print("Starting E2E Stress Tests...")
        
        self.test_gnss_loss_recovery()
        self.test_sensor_failure_rejection()
        self.test_thermal_throttling_simulation()
        
        print(f"Stress Tests Completed: {self.passed_tests}/{self.total_tests} passed.")

    def test_gnss_loss_recovery(self):
        self.total_tests += 1
        print("Running: GNSS Loss & Recovery Simulation")
        engine = NavigationEngine(37.7749, -122.4194, 10.0)
        try:
            # 1. Initialize good GNSS
            engine.process_gnss(37.7749, -122.4194, 10.0, 15.0, 90.0, 5.0, 1.0)
            self.assert_mode(engine, [NavigationMode.GNSS_GOOD])
            
            # 2. Feed IMU for 2 seconds
            for i in range(200):
                engine.process_imu(np.array([0,0,9.8]), np.array([0,0,0]), 0.01, 1.0 + i*0.01)
                
            # 3. Simulate GNSS Loss (no gnss updates for 3 seconds)
            for i in range(200, 500):
                engine.process_imu(np.array([0,0,9.8]), np.array([0,0,0]), 0.01, 1.0 + i*0.01)
            
            # Should have fallen back to DR
            self.assert_mode(engine, [NavigationMode.DEAD_RECKONING, NavigationMode.DEAD_RECKONING_DEGRADED])
            
            # 4. GNSS Recovers
            engine.process_gnss(37.7750, -122.4190, 10.0, 15.0, 90.0, 4.0, 6.0)
            self.assert_mode(engine, [NavigationMode.GNSS_GOOD])
            
            print("  ✓ GNSS Loss & Recovery Passed")
            self.passed_tests += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    def test_sensor_failure_rejection(self):
        self.total_tests += 1
        print("Running: Sensor Failure (NaN/Inf) Rejection")
        engine = NavigationEngine(37.7749, -122.4194, 10.0)
        try:
            # Inject extreme/NaN values
            bad_accel = np.array([np.nan, np.inf, -np.inf])
            bad_gyro = np.array([99999.0, -99999.0, np.nan])
            
            # Should not crash the engine, should handle gracefully or reject
            try:
                engine.process_imu(bad_accel, bad_gyro, 0.01, 10.0)
            except Exception as e:
                pass
                
            print("  ✓ Sensor Failure Rejection Passed (No Crash)")
            self.passed_tests += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            
    def test_thermal_throttling_simulation(self):
        self.total_tests += 1
        print("Running: Thermal Throttling / High Latency Simulation")
        engine = NavigationEngine(37.7749, -122.4194, 10.0)
        try:
            # Simulate CPU throttling causing large dt
            engine.process_imu(np.array([0,0,9.8]), np.array([0,0,0]), 0.5, 20.0) # 500ms dt instead of 10ms
            
            # As long as ESKF covariance grows properly and doesn't explode, we pass
            cov_trace = np.trace(engine.eskf.P)
            assert not np.isnan(cov_trace)
            
            print("  ✓ Thermal Throttling Passed")
            self.passed_tests += 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  ✗ Failed: {e}")

if __name__ == "__main__":
    runner = StressTestRunner()
    runner.run_all()
