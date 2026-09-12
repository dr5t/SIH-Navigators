from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time
from .database import SessionLocal, SessionRecord, TelemetryBatch
from .auth import verify_token, create_access_token
import json

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
        batch_dicts = [p.dict() for p in batch]
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

@app.get("/models/latest")
def get_latest_model():
    """Mock endpoint for Android to download the latest speed estimation model."""
    return {
        "version": "v1.5-fusion",
        "url": "https://storage.example.com/models/v1.5-fusion.pt",
        "checksum": "abc123def456"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
