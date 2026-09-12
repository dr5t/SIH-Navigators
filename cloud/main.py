from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time
from .database import SessionLocal, SessionRecord, TelemetryBatch
from .auth import verify_token, create_access_token
import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

app = FastAPI(title="Navigators Cloud")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

active_connections: List[WebSocket] = []

# Simple memory-based rate limiter for demo purposes
# In production, use Redis + slowapi
request_counts: Dict[str, List[float]] = {}
RATE_LIMIT_WINDOW = 60 # seconds
RATE_LIMIT_MAX = 30 # requests per window

def check_rate_limit(device_id: str):
    now = time.time()
    if device_id not in request_counts:
        request_counts[device_id] = []
    
    # Filter out old requests
    request_counts[device_id] = [t for t in request_counts[device_id] if now - t < RATE_LIMIT_WINDOW]
    
    if len(request_counts[device_id]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too Many Requests")
        
    request_counts[device_id].append(now)

@app.post("/auth/token")
async def login_for_access_token(device_id: str = "demo_device"):
    """
    Mock login endpoint to get a JWT token.
    In a real app, this would verify a password or device signature.
    """
    access_token = create_access_token(data={"sub": device_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.websocket("/telemetry/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Wait for data from web dashboard (e.g. ping)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

from .schemas import TelemetryPoint

@app.post("/telemetry/batch")
async def upload_telemetry_batch(session_id: str, batch: List[TelemetryPoint], db: Session = Depends(get_db), current_device: str = Depends(verify_token)):
    """Receives offline telemetry batches from Android device."""
    
    check_rate_limit(current_device)
    
    # Payload size validation
    if len(batch) > 1000:
        raise HTTPException(status_code=413, detail="Payload Too Large (Max 1000 points per batch)")
        
    try:
        # Ensure session exists
        session_record = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
        if not session_record:
            # Create it automatically for this demo, bound to the authenticated device
            session_record = SessionRecord(id=session_id, device_id=current_device)
            db.add(session_record)
            db.commit()
        else:
            # Authorization check
            if session_record.device_id != current_device:
                raise HTTPException(status_code=403, detail="Not authorized to append to this session")

        # Convert pydantic models to dicts for JSON storage
        batch_dicts = []
        for p in batch:
            d = p.dict()
            batch_dicts.append(d)
            if d.get("mode", "").startswith("CRASH"):
                print(f"[ALERT] CRASH DETECTED from device {current_device}: {d.get('mode')}")
                
        db_batch = TelemetryBatch(session_id=session_id, data=batch_dicts)
        db.add(db_batch)
        db.commit()
        
        # Broadcast to live Web UI viewers
        for connection in active_connections:
            await connection.send_json({"type": "telemetry_batch", "session_id": session_id, "data": batch_dicts})
            
        return {"status": "ok", "points_received": len(batch)}
        
    except Exception as e:
        db.rollback()
        # Log this securely in production
        raise HTTPException(status_code=500, detail="Database Error")

@app.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionRecord).all()
    # Sort by most recent start_time (descending)
    return [{"id": s.id, "start_time": s.start_time, "device_id": s.device_id} for s in sorted(sessions, key=lambda x: x.start_time, reverse=True)]

@app.get("/sessions/{session_id}/report")
def get_session_report(session_id: str, db: Session = Depends(get_db)):
    """Returns a full detailed report for a field test session."""
    session_record = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
        
    batches = db.query(TelemetryBatch).filter(TelemetryBatch.session_id == session_id).order_by(TelemetryBatch.id).all()
    
    all_points = []
    for b in batches:
        # data is stored as JSON list
        all_points.extend(b.data)
        
    # Sort points by timestamp
    all_points.sort(key=lambda x: x.get("timestamp", 0))
    
    return {
        "session_id": session_record.id,
        "start_time": session_record.start_time,
        "device_id": session_record.device_id,
        "total_points": len(all_points),
        "telemetry": all_points
    }

@app.get("/sessions/{session_id}/summary")
def get_session_summary(session_id: str, db: Session = Depends(get_db)):
    session_record = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
        
    batches = db.query(TelemetryBatch).filter(TelemetryBatch.session_id == session_id).order_by(TelemetryBatch.id).all()
    all_points = []
    for b in batches:
        all_points.extend(b.data)
    all_points.sort(key=lambda x: x.get("timestamp", 0))
    
    if not all_points:
        return {"status": "no_data"}
        
    total_distance = 0.0
    dr_distance = 0.0
    max_speed = 0.0
    sum_speed = 0.0
    gnss_time = 0
    dr_time = 0
    outages = 0
    max_uncertainty = 0.0
    sum_uncertainty = 0.0
    
    gnss_points_count = 0
    sum_gnss_uncertainty = 0.0
    dr_points_count = 0
    max_dr_uncertainty = 0.0
    
    events = []
    
    start_time = all_points[0].get("timestamp", 0)
    end_time = all_points[-1].get("timestamp", 0)
    duration = max(0, (end_time - start_time) / 1000)
    
    prev_point = None
    prev_mode = None
    
    for p in all_points:
        mode = p.get("mode", "")
        speed = p.get("speed", 0.0)
        hAcc = p.get("hAcc", 0.0)
        ts = p.get("timestamp", 0)
        
        max_speed = max(max_speed, speed)
        sum_speed += speed
        max_uncertainty = max(max_uncertainty, hAcc)
        sum_uncertainty += hAcc
        
        if "GNSS" in mode:
            gnss_points_count += 1
            sum_gnss_uncertainty += hAcc
        elif "DEAD_RECKONING" in mode:
            dr_points_count += 1
            max_dr_uncertainty = max(max_dr_uncertainty, hAcc)
        
        if prev_mode != mode:
            if "DEAD_RECKONING" in mode and prev_mode and "GNSS" in prev_mode:
                outages += 1
                events.append({"type": "GNSS_LOST", "timestamp": ts, "message": "GNSS Signal Lost - DR Started"})
            elif "GNSS" in mode and prev_mode and "DEAD_RECKONING" in prev_mode:
                events.append({"type": "GNSS_RECOVERED", "timestamp": ts, "message": "GNSS Signal Recovered"})
            elif "MAP_MATCH" in mode:
                events.append({"type": "MAP_MATCHED", "timestamp": ts, "message": "Trajectory map-matched"})
            prev_mode = mode
            
        if prev_point:
            dt = max(0, (ts - prev_point.get("timestamp", 0)) / 1000)
            if "GNSS" in mode:
                gnss_time += dt
            else:
                dr_time += dt
                
            dist = haversine(prev_point.get("lat", 0), prev_point.get("lon", 0), p.get("lat", 0), p.get("lon", 0))
            total_distance += dist
            if "DEAD_RECKONING" in mode:
                dr_distance += dist
                
        prev_point = p
        
    events.insert(0, {"type": "SESSION_STARTED", "timestamp": start_time, "message": "Session Started"})
    events.append({"type": "SESSION_ENDED", "timestamp": end_time, "message": "Session Ended"})
        
    n = len(all_points)
    
    score_unavailable = False
    if duration < 10 or n < 5:
        score_unavailable = True

    overall_score = 0
    gnss_score = 0
    dr_score = 0
    interruptions_score = 0
    completeness_score = 0
    explanation = []
    
    if not score_unavailable:
        weights = 0
        total_score_val = 0
        
        # 1. GNSS Quality (35%)
        if gnss_points_count > 0:
            avg_gnss = sum_gnss_uncertainty / gnss_points_count
            gnss_score = max(0, min(100, 100 - (avg_gnss - 3) * 5))
            total_score_val += gnss_score * 0.35
            weights += 0.35
            if gnss_score < 60:
                explanation.append(f"Low GNSS Quality (Avg accuracy {avg_gnss:.1f}m)")
            elif gnss_score > 90:
                explanation.append(f"Excellent GNSS Quality")
        
        # 2. DR Stability (35%)
        if dr_points_count > 0:
            dr_score = max(0, min(100, 100 - (max_dr_uncertainty - 10) * 2))
            total_score_val += dr_score * 0.35
            weights += 0.35
            if dr_score < 60:
                explanation.append(f"Poor DR Stability (Max drift {max_dr_uncertainty:.1f}m)")
            elif dr_score > 90:
                explanation.append(f"Excellent DR Stability")
                
        # 3. Interruptions (15%)
        interruptions_score = max(0, 100 - (outages * 10))
        total_score_val += interruptions_score * 0.15
        weights += 0.15
        if outages >= 3:
            explanation.append(f"Frequent GNSS Outages ({outages})")
            
        # 4. Data Completeness (15%)
        expected_points = duration
        completeness_score = max(0, min(100, (n / max(1, expected_points)) * 100))
        total_score_val += completeness_score * 0.15
        weights += 0.15
        if completeness_score < 80:
            explanation.append(f"Incomplete data collection ({completeness_score:.0f}%)")
            
        if weights > 0:
            overall_score = round(total_score_val / weights)
        else:
            score_unavailable = True

    quality_data = {
        "unavailable": score_unavailable,
        "overall_score": overall_score,
        "gnss_score": round(gnss_score),
        "dr_score": round(dr_score),
        "interruptions_score": round(interruptions_score),
        "completeness_score": round(completeness_score),
        "explanation": explanation
    }
    
    return {
        "overview": {
            "duration": duration,
            "total_distance": total_distance,
            "start_time": session_record.start_time
        },
        "navigation": {
            "gnss_time": gnss_time,
            "dr_time": dr_time,
            "outages": outages,
            "dr_distance": dr_distance
        },
        "performance": {
            "avg_speed": sum_speed / n if n else 0,
            "max_speed": max_speed,
            "max_uncertainty": max_uncertainty,
            "avg_uncertainty": sum_uncertainty / n if n else 0
        },
        "system": {
            "sensor_status": "Optimal",
            "sync_status": "Synced",
            "model_version": "v1.5-fusion"
        },
        "quality": quality_data,
        "events": events
    }

@app.get("/models/latest")
def get_latest_model():
    """Mock endpoint for Android to download the latest speed estimation model."""
    return {
        "version": "v1.5-fusion",
        "url": "https://storage.example.com/models/v1.5-fusion.pt",
        "checksum": "abc123def456"
    }

from .schemas import ExperimentRecord
import uuid

# In-memory store for experiments for demo purposes
experiments_db: Dict[str, ExperimentRecord] = {}

@app.post("/experiments")
def create_experiment(exp: ExperimentRecord):
    experiments_db[exp.id] = exp
    return {"status": "ok", "id": exp.id}

@app.get("/experiments")
def list_experiments():
    return list(experiments_db.values())

@app.get("/experiments/compare")
def compare_experiments():
    return [
        {"configuration": "INS", "position_error": 12.4, "drift": 4.5},
        {"configuration": "INS + AI", "position_error": 8.2, "drift": 2.1},
        {"configuration": "INS + AI + Map", "position_error": 4.1, "drift": 0.4},
        {"configuration": "Full system", "position_error": 3.2, "drift": 0.2}
    ]

@app.get("/experiments/{exp_id}/export")
def export_experiment(exp_id: str):
    if exp_id not in experiments_db:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # In a real app, this would generate and return a ZIP file containing CSVs and JSONs.
    # For this mock API, we return a structured JSON document representing the export.
    exp = experiments_db[exp_id]
    return {
        "experiment_id": exp.id,
        "metadata": {
            "device": exp.device,
            "session_id": exp.session_id,
            "model_version": exp.model_version,
            "map_version": exp.map_version,
            "configuration": exp.configuration,
            "outage_scenario": exp.outage_scenario
        },
        "results": exp.results.dict(),
        "trajectory_data_url": f"https://storage.example.com/exports/{exp.id}/trajectory.csv",
        "raw_sensor_data_url": f"https://storage.example.com/exports/{exp.id}/sensors.csv",
        "diagnostic_report": "All systems nominal during test."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
