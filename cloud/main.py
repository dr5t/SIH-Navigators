from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .database import SessionLocal, SessionRecord, TelemetryBatch
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

@app.post("/telemetry/batch")
async def upload_telemetry_batch(session_id: str, batch: List[Dict[str, Any]], db: Session = Depends(get_db)):
    """Receives offline telemetry batches from Android device."""
    # Ensure session exists
    session_record = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session_record:
        # Create it automatically for this demo
        session_record = SessionRecord(id=session_id, device_id="android_client")
        db.add(session_record)
        db.commit()

    db_batch = TelemetryBatch(session_id=session_id, data=batch)
    db.add(db_batch)
    db.commit()
    
    # Broadcast to live Web UI viewers
    for connection in active_connections:
        await connection.send_json({"type": "telemetry_batch", "session_id": session_id, "data": batch})
        
    return {"status": "ok", "points_received": len(batch)}

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
    
    # Calculate some summary stats
    total_distance = 0.0
    # In a full implementation, distance would be computed using haversine between GNSS points
    
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
