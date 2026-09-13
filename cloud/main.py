from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time
from database import SessionLocal, SessionRecord, TelemetryBatch, VehicleProfile, ExperimentRecord, FeedbackReport
from schemas import VehicleProfileCreate, VehicleProfileUpdate, VehicleProfileResponse, ExperimentRecord as ExperimentRecordSchema, FeedbackReportCreate, FeedbackReportResponse, FeedbackStatusUpdate
from auth import verify_token, create_access_token
import json
import math
import uuid

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

from schemas import TelemetryPoint

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

@app.get("/sessions/{session_id}/export")
def export_session(session_id: str, db: Session = Depends(get_db)):
    from export import generate_export
    try:
        zip_buffer = generate_export(session_id, db)
        return StreamingResponse(
            zip_buffer, 
            media_type="application/zip", 
            headers={"Content-Disposition": f"attachment; filename=session_{session_id}_export.zip"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

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
    
    gap_time = 0.0
    backward_jumps = 0
    ai_missing_in_dr_time = 0.0
    
    prev_point = None
    prev_mode = None
    prev_map_matched = False
    prev_low_confidence = False
    
    events.append({
        "timestamp": start_time,
        "type": "SESSION_STARTED",
        "category": "System",
        "severity": "INFO",
        "description": "Session Started",
        "measurements": None
    })
    
    for p in all_points:
        mode = p.get("mode", "")
        speed = p.get("speed", 0.0)
        hAcc = p.get("h_acc", p.get("hAcc", 0.0))
        ts = p.get("timestamp", 0)
        conf = p.get("map_match_confidence", 0.0)
        
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
        
        # Detailed Event Inference
        if prev_mode != mode:
            if "DEAD_RECKONING" in mode and prev_mode and "GNSS" in prev_mode:
                outages += 1
                events.append({"timestamp": ts, "type": "GNSS_LOST", "category": "GNSS", "severity": "ERROR", "description": "GNSS lost", "measurements": {"accuracy": f"{hAcc:.1f}m"}})
                events.append({"timestamp": ts, "type": "DR_STARTED", "category": "DR", "severity": "WARNING", "description": "DR started", "measurements": {"speed": f"{speed:.1f}m/s"}})
            elif "GNSS" in mode and prev_mode and "DEAD_RECKONING" in prev_mode:
                events.append({"timestamp": ts, "type": "GNSS_RECOVERED", "category": "GNSS", "severity": "SUCCESS", "description": "GNSS recovered", "measurements": {"accuracy": f"{hAcc:.1f}m"}})
                # Fusion typically integrates the recovered GNSS signal
                events.append({"timestamp": ts + 3000, "type": "FUSION_COMPLETED", "category": "Fusion", "severity": "SUCCESS", "description": "Fusion completed", "measurements": None})
            elif "GNSS_DEGRADED" in mode and prev_mode and "GNSS_GOOD" in prev_mode:
                events.append({"timestamp": ts, "type": "GNSS_DEGRADED", "category": "GNSS", "severity": "WARNING", "description": "GNSS degraded", "measurements": {"accuracy": f"{hAcc:.1f}m"}})
            elif "GNSS_GOOD" in mode and (prev_mode == "INITIALIZING" or prev_mode is None):
                events.append({"timestamp": ts, "type": "GNSS_ACQUIRED", "category": "GNSS", "severity": "SUCCESS", "description": "GNSS acquired", "measurements": {"accuracy": f"{hAcc:.1f}m"}})
            
            prev_mode = mode
            
        # Map Matching Events
        is_map_matched = (conf is not None and conf > 0.3)
        if is_map_matched and not prev_map_matched:
            events.append({"timestamp": ts, "type": "MAP_MATCHED", "category": "Map", "severity": "INFO", "description": "Map matched", "measurements": {"confidence": f"{conf:.2f}"}})
        prev_map_matched = is_map_matched
        
        # Low Confidence Events
        is_low_confidence = hAcc > 20.0 or ("DEGRADED" in mode and "DEAD_RECKONING" in mode)
        if is_low_confidence and not prev_low_confidence:
            events.append({"timestamp": ts, "type": "LOW_CONFIDENCE", "category": "Errors", "severity": "WARNING", "description": "Low confidence", "measurements": {"accuracy": f"{hAcc:.1f}m"}})
        prev_low_confidence = is_low_confidence
            
        if prev_point:
            raw_dt = (ts - prev_point.get("timestamp", 0)) / 1000.0
            if raw_dt < 0:
                backward_jumps += 1
            elif raw_dt > 2.0:
                gap_time += raw_dt
                
            dt = max(0, raw_dt)
            if "GNSS" in mode:
                gnss_time += dt
            else:
                dr_time += dt
                if p.get("ai_speed") is None and p.get("aiSpeed") is None:
                    ai_missing_in_dr_time += dt
                
            dist = haversine(prev_point.get("lat", 0), prev_point.get("lon", 0), p.get("lat", 0), p.get("lon", 0))
            total_distance += dist
            if "DEAD_RECKONING" in mode:
                dr_distance += dist
                
        prev_point = p
        
    events.append({
        "timestamp": end_time,
        "type": "SESSION_ENDED",
        "category": "System",
        "severity": "INFO",
        "description": "Session Ended",
        "measurements": None
    })
        
    events.sort(key=lambda e: e.get("timestamp", 0))
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

    # Quality Analysis
    quality_status = "NORMAL USE"
    quality_reasons = []
    
    gap_percent = (gap_time / max(1, duration)) * 100
    
    if duration < 10 or n < 5 or gap_percent > 50:
        quality_status = "INSUFFICIENT DATA"
        quality_reasons.append("Session too short or missing too much data")
    else:
        if gap_percent > 10.0:
            quality_reasons.append(f"{gap_percent:.0f}% sensor data gap")
        if dr_time > 60.0:
            quality_reasons.append(f"GNSS unavailable for {dr_time:.0f} s")
        if backward_jumps > 0:
            quality_reasons.append(f"{backward_jumps} backward timestamp jumps detected")
        if ai_missing_in_dr_time > 10.0:
            quality_reasons.append(f"AI speed unavailable during {ai_missing_in_dr_time:.0f} s")
            
        if len(quality_reasons) > 0:
            quality_status = "REVIEW RECOMMENDED"

    quality_data = {
        "unavailable": score_unavailable,
        "overall_score": overall_score,
        "gnss_score": round(gnss_score),
        "dr_score": round(dr_score),
        "interruptions_score": round(interruptions_score),
        "completeness_score": round(completeness_score),
        "explanation": explanation,
        "analysis_status": quality_status,
        "analysis_reasons": quality_reasons
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

import uuid

@app.post("/experiments")
def create_experiment(exp: ExperimentRecordSchema, db: Session = Depends(get_db)):
    db_exp = ExperimentRecord(
        id=exp.id,
        timestamp=exp.timestamp,
        device=exp.device,
        session_id=exp.session_id,
        model_version=exp.model_version,
        map_version=exp.map_version,
        configuration=exp.configuration,
        outage_scenario=exp.outage_scenario,
        results=exp.results.dict()
    )
    db.add(db_exp)
    db.commit()
    return {"status": "ok", "id": exp.id}

@app.get("/experiments")
def list_experiments(db: Session = Depends(get_db)):
    exps = db.query(ExperimentRecord).order_by(ExperimentRecord.timestamp.desc()).all()
    # Format the results column properly since it might be serialized as string depending on DB driver
    out = []
    for exp in exps:
        r = exp.results
        if isinstance(r, str):
            r = json.loads(r)
        out.append({
            "id": exp.id,
            "session_id": exp.session_id,
            "configuration": exp.configuration,
            "results": r,
            "timestamp": exp.timestamp
        })
    return out

@app.post("/sessions/{session_id}/replay")
def run_replay(session_id: str, payload: dict, db: Session = Depends(get_db)):
    config = payload.get("configuration", "INS")
    model_version = payload.get("model_version", "v1.4")
    from replay import run_experiment
    try:
        return run_experiment(session_id, config, model_version, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/experiments/compare")
def compare_experiments(exp_a: str, exp_b: str, db: Session = Depends(get_db)):
    # Compares two experiments from DB
    a = db.query(ExperimentRecord).filter(ExperimentRecord.id == exp_a).first()
    b = db.query(ExperimentRecord).filter(ExperimentRecord.id == exp_b).first()
    if not a or not b:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    ra = a.results if not isinstance(a.results, str) else json.loads(a.results)
    rb = b.results if not isinstance(b.results, str) else json.loads(b.results)
    
    return {
        "experiment_a": {"id": a.id, "session_id": a.session_id, "model_version": a.model_version, "configuration": a.configuration, "results": ra},
        "experiment_b": {"id": b.id, "session_id": b.session_id, "model_version": b.model_version, "configuration": b.configuration, "results": rb}
    }

@app.get("/experiments/{exp_id}/export")
def export_experiment(exp_id: str, db: Session = Depends(get_db)):
    exp = db.query(ExperimentRecord).filter(ExperimentRecord.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # In a real app, this would generate and return a ZIP file containing CSVs and JSONs.
    # For this mock API, we return a structured JSON document representing the export.
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
        "results": exp.results if not isinstance(exp.results, str) else json.loads(exp.results),
        "trajectory_data_url": f"https://storage.example.com/exports/{exp.id}/trajectory.csv",
        "raw_sensor_data_url": f"https://storage.example.com/exports/{exp.id}/sensors.csv",
        "diagnostic_report": "All systems nominal during test."
    }

# Profiles Endpoints

@app.get("/profiles", response_model=List[VehicleProfileResponse])
def get_profiles(device_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    return db.query(VehicleProfile).filter(VehicleProfile.device_id == device_id).all()

@app.post("/profiles", response_model=VehicleProfileResponse)
def create_profile(profile: VehicleProfileCreate, device_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    profile_id = str(uuid.uuid4())
    db_profile = VehicleProfile(
        id=profile_id,
        device_id=device_id,
        name=profile.name,
        vehicle_type=profile.vehicle_type,
        phone_mounting=profile.phone_mounting,
        external_imu=1 if profile.external_imu else 0,
        nav_prefs=profile.nav_prefs
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    # Convert integer boolean back for Pydantic response
    db_profile.is_calibrated = bool(db_profile.is_calibrated)
    db_profile.external_imu = bool(db_profile.external_imu)
    return db_profile

@app.put("/profiles/{profile_id}", response_model=VehicleProfileResponse)
def update_profile(profile_id: str, profile_update: VehicleProfileUpdate, device_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    db_profile = db.query(VehicleProfile).filter(VehicleProfile.id == profile_id, VehicleProfile.device_id == device_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    update_data = profile_update.dict(exclude_unset=True)
    if 'is_calibrated' in update_data:
        update_data['is_calibrated'] = 1 if update_data['is_calibrated'] else 0
    if 'external_imu' in update_data:
        update_data['external_imu'] = 1 if update_data['external_imu'] else 0
        
    for key, value in update_data.items():
        setattr(db_profile, key, value)
        
    db.commit()
    db.refresh(db_profile)
    
    db_profile.is_calibrated = bool(db_profile.is_calibrated)
    db_profile.external_imu = bool(db_profile.external_imu)
    return db_profile

@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str, device_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    db_profile = db.query(VehicleProfile).filter(VehicleProfile.id == profile_id, VehicleProfile.device_id == device_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(db_profile)
    db.commit()
    return {"status": "deleted"}

@app.post("/feedback", response_model=FeedbackReportResponse)
def submit_feedback(report: FeedbackReportCreate, device_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    import datetime
    year = datetime.datetime.now().year
    
    # Simple ID generation NAV-YYYY-UUID(first 6)
    short_uuid = str(uuid.uuid4())[:6].upper()
    report_id = f"NAV-{year}-{short_uuid}"
    
    db_report = FeedbackReport(
        id=report_id,
        device_id=device_id,
        category=report.category,
        description=report.description,
        severity=report.severity,
        session_id=report.session_id,
        technical_context=report.technical_context,
        rating=report.rating
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report

@app.get("/feedback", response_model=List[FeedbackReportResponse])
def get_feedback(
    status: str = None, 
    category: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
):
    # In a real system, require admin token here. For this demo, open endpoint for dashboard.
    query = db.query(FeedbackReport)
    
    if status:
        query = query.filter(FeedbackReport.status == status)
    if category:
        query = query.filter(FeedbackReport.category == category)
    if severity:
        query = query.filter(FeedbackReport.severity == severity)
        
    return query.order_by(FeedbackReport.created_at.desc()).all()

@app.get("/feedback/analytics")
def get_feedback_analytics(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total = db.query(FeedbackReport).count()
    open_count = db.query(FeedbackReport).filter(FeedbackReport.status.in_(["Submitted", "Under Review", "Investigating"])).count()
    resolved = db.query(FeedbackReport).filter(FeedbackReport.status.in_(["Resolved", "Closed"])).count()
    
    by_category = db.query(FeedbackReport.category, func.count(FeedbackReport.id)).group_by(FeedbackReport.category).all()
    by_severity = db.query(FeedbackReport.severity, func.count(FeedbackReport.id)).group_by(FeedbackReport.severity).all()
    
    return {
        "total_reports": total,
        "open_reports": open_count,
        "resolved_reports": resolved,
        "by_category": [{"category": c, "count": cnt} for c, cnt in by_category],
        "by_severity": [{"severity": s, "count": cnt} for s, cnt in by_severity]
    }

@app.get("/feedback/{report_id}", response_model=FeedbackReportResponse)
def get_feedback_detail(report_id: str, db: Session = Depends(get_db)):
    report = db.query(FeedbackReport).filter(FeedbackReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.put("/feedback/{report_id}/status", response_model=FeedbackReportResponse)
def update_feedback_status(report_id: str, status_update: FeedbackStatusUpdate, db: Session = Depends(get_db)):
    report = db.query(FeedbackReport).filter(FeedbackReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    valid_statuses = ["Submitted", "Under Review", "Investigating", "Resolved", "Closed"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    report.status = status_update.status
    db.commit()
    db.refresh(report)
    
    return report



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
