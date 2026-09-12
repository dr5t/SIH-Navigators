from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Navigators Backend API")

class TrajectoryPoint(BaseModel):
    timestamp: float
    lat: float
    lon: float
    alt: float
    speed: float
    heading: float

class SessionData(BaseModel):
    session_id: str
    device_id: str
    trajectory: List[TrajectoryPoint]

# In-memory store for extreme efficiency
db: Dict[str, SessionData] = {}

@app.post("/api/v1/sync")
async def sync_session(data: SessionData):
    """Offline-first sync endpoint for uploading recorded sessions."""
    db[data.session_id] = data
    return {"status": "success", "message": f"Session {data.session_id} synced."}

@app.get("/api/v1/sessions")
async def list_sessions():
    """Retrieve all uploaded session IDs."""
    return {"sessions": list(db.keys())}

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Retrieve a specific trajectory for the dashboard."""
    if session_id not in db:
        raise HTTPException(status_code=404, detail="Session not found")
    return db[session_id]
