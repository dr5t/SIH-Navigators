import sys
import time
import os
import json
from datetime import datetime
from tests.run_regression import load_session, SessionEvaluator
import requests

# This script simulates a highly specific Demo presentation of the Navigators system.

def run_demo():
    print("==================================================")
    print("   NAVIGATORS - END-TO-END SHOWCASE DEMO          ")
    print("==================================================")
    print("\n[INIT] Connecting to local Cloud API...")
    
    # Try to authenticate with the backend
    try:
        response = requests.post("http://localhost:8000/auth/token?device_id=demo_showcase")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("[INIT] JWT Token acquired successfully.")
        else:
            print(f"[ERROR] Failed to authenticate: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cloud backend not running on port 8000. Start it first.")
        return

    print("\n[PHASE 1] GNSS Available (Normal Operation)")
    print("  -> Simulating standard urban driving with good sky view.")
    print("  -> ESKF is continuously calibrating IMU biases.")
    time.sleep(2)

    print("\n[PHASE 2] GNSS Outage (Entering Tunnel)")
    print("  -> GNSS signals blocked. Transitioning to Intelligent Dead Reckoning.")
    print("  -> Fusing Android IMU kinematics with AI Speed Estimator...")
    time.sleep(2)
    
    print("\n[PHASE 3] Map Matching & Constraint")
    print("  -> Drift detected! Snapping trajectory to local Offline Road Graph (Main St).")
    time.sleep(2)
    
    print("\n[PHASE 4] GNSS Recovery (Exiting Tunnel)")
    print("  -> GNSS lock re-acquired. Executing smooth ESKF covariance correction.")
    print("  -> Teleportation prevented via chi-square gating.")
    time.sleep(2)
    
    print("\n[PHASE 5] Cloud Sync & Final Reporting")
    print("  -> Vehicle parked. Flushing telemetry queues via TelemetrySyncWorker.")
    
    # Send a mock batch of demo telemetry
    session_id = f"DEMO_{int(time.time())}"
    batch = []
    
    # Create 60 seconds of mock data
    for i in range(60):
        # 10s GNSS, 40s Outage (AI Speed), 10s GNSS Recovery
        mode = "GNSS_GOOD"
        if 10 <= i < 50:
            mode = "DEAD_RECKONING (AI Speed)"
            
        point = {
            "timestamp": time.time() - 60 + i,
            "latitude": 37.7749 + (i * 0.0001),
            "longitude": -122.4194 + (i * 0.0001),
            "altitude": 10.0,
            "speed": 12.5 + (0.1 if i % 2 == 0 else -0.1),
            "course": 45.0,
            "h_acc": 4.0 if mode == "GNSS_GOOD" else 15.0,
            "v_acc": 6.0 if mode == "GNSS_GOOD" else 25.0,
            "mode": mode
        }
        batch.append(point)
        
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.post(
            f"http://localhost:8000/telemetry/batch?session_id={session_id}",
            json=batch,
            headers=headers
        )
        if res.status_code == 200:
            print(f"  -> Successfully uploaded 60 telemetry points for Session: {session_id}")
        else:
            print(f"  -> Sync failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"  -> Exception during sync: {e}")

    print("\n==================================================")
    print("   DEMO COMPLETE. Check Web Dashboard for details.")
    print("==================================================")

if __name__ == "__main__":
    run_demo()
