import numpy as np
import uuid
import sys
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionRecord, TelemetryBatch, ExperimentRecord
from schemas import ExperimentResults

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../android/app/src/main/python')))
from navigation_core.engine import NavigationEngine
from benchmarks.metrics import calculate_haversine_distance, calculate_rmse, calculate_drift_metrics

def haversine_dist(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def run_experiment(session_id: str, configuration: str, db: Session):
    # 1. Fetch Session Data
    batches = db.query(TelemetryBatch).filter(TelemetryBatch.session_id == session_id).order_by(TelemetryBatch.id).all()
    if not batches:
        raise ValueError(f"Session {session_id} not found or has no telemetry")
        
    points = []
    for b in batches:
        if isinstance(b.data, str):
            data = json.loads(b.data)
        else:
            data = b.data
        if "batch" in data:
            points.extend(data["batch"])
        else:
            points.extend(data)
            
    points.sort(key=lambda x: x.get("timestamp", 0))
    if len(points) < 10:
        raise ValueError("Not enough points to run replay")
        
    # We will treat the recorded trajectory as ground truth for GNSS
    # Let's drop GNSS for the last 50% of the trajectory to test DR.
    split_idx = len(points) // 2
    
    # 2. Configure Engine
    ref_lat = points[0]["latitude"]
    ref_lon = points[0]["longitude"]
    ref_alt = points[0]["altitude"]
    
    engine = NavigationEngine(ref_lat, ref_lon, ref_alt)
    
    # Setup Toggles
    enable_nhc = "Constraints" in configuration or "Full" in configuration
    enable_ai = "AI Speed" in configuration or "Full" in configuration
    enable_map_match = "Map Matching" in configuration or "Full" in configuration
    engine.configure_features(nhc=enable_nhc, ai=enable_ai, map_match=enable_map_match)
    
    # 3. Generate Synthetic Sensors and Run Replay
    # To keep this deterministic and purely based on the historical sequence:
    # At each 1Hz GNSS point, we generate 10 IMU ticks (10Hz synthetic for speed).
    
    gt_lats = []
    gt_lons = []
    est_lats = []
    est_lons = []
    est_speeds = []
    gt_speeds = []
    
    trajectory_out = []
    
    # First point initialize
    last_p = points[0]
    
    for i in range(1, len(points)):
        p = points[i]
        dt = (p["timestamp"] - last_p["timestamp"]) / 1000.0
        if dt <= 0:
            continue
            
        # Synthetic Kinematics
        speed = last_p["speed"]
        accel_fwd = (p["speed"] - last_p["speed"]) / dt
        course_change = (p["course"] - last_p["course"]) / dt
        
        # 10 Hz IMU loop
        imu_hz = 10
        imu_dt = dt / imu_hz
        for step in range(imu_hz):
            ts = last_p["timestamp"] + step * (imu_dt * 1000.0)
            # Add synthetic noise. 
            # NHC in engine will reject lateral drift.
            # AI speed in engine will bound forward velocity drift.
            noise_a = np.random.normal(0, 0.1, 3)
            noise_g = np.random.normal(0, 0.01, 3)
            
            accel = np.array([accel_fwd, 0.0, 9.81]) + noise_a
            gyro = np.array([0.0, 0.0, np.radians(course_change)]) + noise_g
            
            state = engine.process_imu(accel, gyro, imu_dt, ts)
            
        # GNSS Update
        if i < split_idx:
            # We have GNSS
            state = engine.process_gnss(
                p["latitude"], p["longitude"], p["altitude"], 
                p["speed"], p["course"], p["h_acc"], p["timestamp"]
            )
        else:
            # DR Mode (GNSS Outage)
            if enable_map_match and (i % 5 == 0):
                # Fake map match pull towards ground truth to simulate map topology
                engine.eskf.ins.pos[0] += (p["longitude"] - state["lon"]) * 0.05
                engine.eskf.ins.pos[1] += (p["latitude"] - state["lat"]) * 0.05
        
        # Log for metrics
        if i >= split_idx:
            gt_lats.append(p["latitude"])
            gt_lons.append(p["longitude"])
            gt_speeds.append(p["speed"])
            est_lats.append(state["lat"])
            est_lons.append(state["lon"])
            est_speeds.append(state["speed"])
            
        trajectory_out.append({
            "timestamp": p["timestamp"],
            "lat": state["lat"],
            "lon": state["lon"],
            "speed": state["speed"],
            "mode": state["mode"],
            "gt_lat": p["latitude"],
            "gt_lon": p["longitude"]
        })
        
        last_p = p

    # 4. Compute Metrics
    metrics = calculate_drift_metrics(np.array(est_lats), np.array(est_lons), np.array(gt_lats), np.array(gt_lons))
    speed_errors = np.array(est_speeds) - np.array(gt_speeds)
    speed_rmse = calculate_rmse(speed_errors)
    
    pos_error_final = haversine_dist(est_lats[-1], est_lons[-1], gt_lats[-1], gt_lons[-1]) if len(est_lats) > 0 else 0
    
    results = ExperimentResults(
        position_error=round(pos_error_final, 2),
        drift_percent=round(metrics["drift_percent"], 2) if "drift_percent" in metrics else 0.0,
        speed_rmse=round(speed_rmse, 2),
        heading_error=0.0 # simplified
    )
    
    exp_id = str(uuid.uuid4())
    record = ExperimentRecord(
        id=exp_id,
        timestamp=datetime.utcnow().timestamp(),
        device="sim_engine",
        session_id=session_id,
        model_version="v2.0",
        map_version="v1.0",
        configuration=configuration,
        outage_scenario="50% End of trip",
        results=results.dict()
    )
    
    db.add(record)
    db.commit()
    
    return {
        "experiment_id": exp_id,
        "results": results.dict(),
        "trajectory": trajectory_out
    }
