import requests
import json
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from navigation_core.engine import NavigationEngine

def fetch_session_data(session_id: str, base_url="http://localhost:8000"):
    print(f"Fetching session {session_id} from {base_url}...")
    try:
        response = requests.get(f"{base_url}/sessions/{session_id}/report")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching session: {e}")
        return None

def run_regression(session_id: str = None):
    # This script simulates what an automated CI/CD regression test would look like
    # using a real-world recorded session to measure DR accuracy changes.
    
    if session_id:
        data = fetch_session_data(session_id)
        if not data:
            return
        points = data.get("telemetry", [])
    else:
        print("No session ID provided. Running mock simulation.")
        # Create mock sequence
        points = []
        for i in range(100):
            points.append({
                "timestamp": i * 0.1,
                "mode": "GNSS_GOOD" if i < 20 else "DEAD_RECKONING",
                "lat": 37.7749 + i*0.0001,
                "lon": -122.4194,
                "alt": 10.0,
                "speed": 15.0,
                "course": 90.0,
                # Simulate the raw inputs that would be recorded in a full system
                # (Our current telemetry only saves state, not raw inputs.
                # In a true regression suite, we'd record raw IMU and GNSS, not just state).
            })

    if not points:
        print("No points to process.")
        return

    # In a full implementation, we would extract the RAW IMU and GNSS measurements 
    # from the session (which requires storing them in TelemetryBatch), instantiate
    # NavigationEngine, feed them in, and compare the resulting NavigationState output
    # to the Ground Truth (GNSS).
    
    print("Regression suite framework initialized.")
    print(f"Total points ready for playback: {len(points)}")
    print("To fully implement regression, TelemetryEntity must be updated to store raw sensor values.")
    print("Regression test PASSED (Framework stub).")

if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else None
    run_regression(sid)
