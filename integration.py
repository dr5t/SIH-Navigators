import numpy as np
import httpx
import asyncio
from edge.engine import EdgeEngine
from replay.engine import ReplayEngine
from ml.datasets.io_vnbd import ImuData, GnssData

def run_integration():
    """
    Simulates a full system run:
    1. Loads a dataset (dummy for now).
    2. Runs it through the Edge Engine (ESKF + constraints + ML).
    3. Syncs the resulting trajectory to the FastAPI backend.
    """
    # 1. Create dummy data
    N = 100
    timestamps = np.linspace(0, 1.0, N)
    accel = np.ones((N, 3)) * np.array([0, 0, 9.81])
    gyro = np.zeros((N, 3))
    
    imu_data = ImuData(timestamps, accel, gyro, None)
    gnss_data = GnssData(np.array([0.0]), np.array([37.7]), np.array([-122.4]), 
                         np.array([10.0]), np.array([0.0]), np.array([0.0]), 
                         np.array([1.0]))
    
    # 2. Initialize Edge Engine
    from navigation_core.engine import NavigationEngine
    edge = NavigationEngine(37.7, -122.4, 10.0)
    
    trajectory = []
    
    def nav_callback(imu_sample, gnss):
        state = edge.process_imu(imu_sample['accel'], imu_sample['gyro'], 0.01, imu_sample['timestamp'])
        
        # If GNSS is available at this timestamp, process it
        if len(gnss.timestamp) > 0 and abs(gnss.timestamp[0] - imu_sample['timestamp']) < 0.01:
            speed = gnss.speed[0]
            bearing = gnss.bearing[0]
            
            state = edge.process_gnss(gnss.lat[0], gnss.lon[0], gnss.alt[0], 
                               speed, bearing, gnss.accuracy[0], gnss.timestamp[0])
            
        trajectory.append(state)
            
    # 3. Replay through engine
    replay = ReplayEngine(imu_data, gnss_data, nav_callback)
    print("Running Engine simulation...")
    replay.play(speed=0)  # Run as fast as possible
    
    # 4. Extract trajectory and sync to backend
    payload = {
        "session_id": "sim_session_001",
        "device_id": "sim_device",
        "trajectory": [
            {
                "timestamp": pt['timestamp'],
                "lat": pt['lat'],
                "lon": pt['lon'],
                "alt": pt['alt'],
                "speed": pt['speed'],
                "heading": pt['course']
            } for pt in trajectory
        ]
    }
    
    print(f"Generated {len(traj)} trajectory points. Syncing to backend...")
    
    try:
        response = httpx.post("http://localhost:8000/api/v1/sync", json=payload)
        print("Backend response:", response.json())
    except Exception as e:
        print("Failed to sync to backend. Is it running? Error:", e)

if __name__ == "__main__":
    run_integration()
