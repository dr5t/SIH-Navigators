import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from navigation_core.engine import NavigationEngine
from navigation_core.fusion.state_machine import NavigationMode

def test_gnss_robustness_flow():
    # Initialize Engine at a fixed point
    ref_lat, ref_lon, ref_alt = 37.7749, -122.4194, 10.0
    engine = NavigationEngine(ref_lat, ref_lon, ref_alt)
    
    current_time = 0.0
    
    lon_offset_m = 0.0
    
    # helper for processing GNSS and checking mode
    def apply_gnss(lat_offset, lon_offset, alt_offset, speed, h_acc, expect_mode):
        nonlocal current_time
        current_time += 1.0
        # IMU tick (just to keep engine alive)
        engine.process_imu(np.array([0,0,9.81]), np.array([0,0,0]), 1.0, current_time)
        
        # GNSS tick
        state = engine.process_gnss(
            ref_lat + lat_offset, 
            ref_lon + lon_offset, 
            ref_alt + alt_offset, 
            speed, 90.0, h_acc, current_time
        )
        print(f"Time {current_time}: Expected {expect_mode.name}, Got {state['mode']}")
        assert state["mode"] == expect_mode.name, f"Expected {expect_mode.name}, got {state['mode']}"
        return state

    # STAGE 1: GOOD GNSS
    # Feed 3 good updates to converge the filter (moving 15m/s East)
    for _ in range(3):
        lon_offset_m += 15.0
        lon_deg = lon_offset_m / (111000.0 * np.cos(np.radians(ref_lat)))
        apply_gnss(0.0001, lon_deg, 0.0, 15.0, 2.0, NavigationMode.GNSS_GOOD)
        
    base_pos_uncertainty = engine.last_state.pos_uncertainty

    # STAGE 2: NOISY GNSS (Adaptive weighting)
    lon_offset_m += 15.0
    lon_deg = lon_offset_m / (111000.0 * np.cos(np.radians(ref_lat)))
    # Add an additional 5 meter jump which is within chi-square inflation bounds (15-50)
    lon_deg += 5.0 / (111000.0 * np.cos(np.radians(ref_lat)))
    state_noisy = apply_gnss(0.0001, lon_deg, 0.0, 15.0, 5.0, NavigationMode.GNSS_GOOD)
    # Uncertainty should increase or remain high due to adaptive weighting vs a normal good fix
    
    # STAGE 3: OUTLIER (Rejection)
    # A massive jump (teleportation) should be rejected completely.
    state_outlier = apply_gnss(0.05, 0.0, 0.0, 15.0, 5.0, NavigationMode.GNSS_REJECTED)
    
    # STAGE 4: GNSS LOST (Enter DR)
    current_time += 3.0 # Simulate 3 second gap
    engine.process_imu(np.array([0,0,9.81]), np.array([0,0,0]), 3.0, current_time)
    assert engine.last_state.mode == NavigationMode.DEAD_RECKONING

    # STAGE 5: GNSS RETURNS WITH BAD FIX (Verify rejection, remain in DR)
    # Simulating returning from tunnel but the first fix is garbage
    apply_gnss(0.02, 0.0, 0.0, 15.0, 15.0, NavigationMode.GNSS_REJECTED)
    
    # Need consecutive good fixes to recover from DR
    # STAGE 6: GOOD GNSS RETURNS (Recovery)
    # First good fix might still be rejected due to recovery validation needing 3 consecutive
    # Wait, time in DR is < 10 seconds (it was 3s), so it shouldn't need 3 consecutive fixes unless it was a long outage.
    # But wait, it might still reject it if it's too far from DR. Let's provide a fix very close to DR state.
    
    # Let's give a fix exactly where the INS thinks it is
    current_lat = engine.last_state.latitude
    current_lon = engine.last_state.longitude
    
    # 1st good fix - might still be GNSS_REJECTED if chi-square was high, but since it matches INS, should be GOOD.
    state_recovery = engine.process_gnss(
        current_lat, current_lon, ref_alt, 15.0, 90.0, 2.0, current_time + 1.0
    )
    assert state_recovery["mode"] == NavigationMode.GNSS_GOOD.name

    print("Robustness test passed successfully.")

if __name__ == "__main__":
    test_gnss_robustness_flow()
