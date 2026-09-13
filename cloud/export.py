import io
import csv
import json
import zipfile
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionRecord, TelemetryBatch, ExperimentRecord

SCHEMA_DOCS = """# Navigators Session Export

This package contains data for a completed navigation session.

## Files Included:
- `session.json`: Basic session metadata (start time, device ID).
- `metadata.json`: Additional app/model configurations.
- `navigation.csv`: The core estimated trajectory from the engine.
- `gnss.csv`: Raw GNSS measurements (if available).
- `ai_speed.csv`: AI speed constraint telemetry (if available).
- `events.json`: Chronological timeline of navigation events.
- `diagnostics.json`: Hardware/System diagnostic events.
- `schema_docs.txt`: This file.

## Privacy Notice
This export contains sensitive location and timestamp data. Do not share this package publicly unless you have scrubbed personal identifying locations (e.g., home/work).
"""

def generate_export(session_id: str, db: Session) -> io.BytesIO:
    # 1. Fetch data
    session_record = db.query(SessionRecord).filter(SessionRecord.id == session_id).first()
    if not session_record:
        raise ValueError(f"Session {session_id} not found")
        
    batches = db.query(TelemetryBatch).filter(TelemetryBatch.session_id == session_id).order_by(TelemetryBatch.id).all()
    experiments = db.query(ExperimentRecord).filter(ExperimentRecord.session_id == session_id).all()
    
    # 2. Parse telemetry
    points = []
    events = []
    diagnostics = []
    
    for b in batches:
        data = b.data if not isinstance(b.data, str) else json.loads(b.data)
        if "batch" in data:
            points.extend(data["batch"])
        else:
            points.extend(data)
            
    # Typically events and diagnostics might be stored in the session metadata or a separate table
    # For now, let's extract them if they are in the session_record metadata
    metadata = session_record.metadata_json if session_record.metadata_json else {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
        
    events = metadata.get("events", [])
    diagnostics = metadata.get("diagnostics", [])
    
    # Sort points
    points.sort(key=lambda x: x.get("timestamp", 0))

    # 3. Create CSV buffers
    nav_csv = io.StringIO()
    nav_writer = csv.writer(nav_csv)
    nav_writer.writerow(["timestamp", "lat", "lon", "alt", "speed", "heading", "mode", "confidence"])

    gnss_csv = io.StringIO()
    gnss_writer = csv.writer(gnss_csv)
    gnss_writer.writerow(["timestamp", "lat", "lon", "alt", "speed", "heading", "h_acc", "v_acc"])
    
    ai_csv = io.StringIO()
    ai_writer = csv.writer(ai_csv)
    ai_writer.writerow(["timestamp", "speed_limit", "confidence"])

    for p in points:
        ts = p.get("timestamp", 0)
        nav_writer.writerow([
            ts,
            p.get("latitude", 0),
            p.get("longitude", 0),
            p.get("altitude", 0),
            p.get("speed", 0),
            p.get("course", 0),
            p.get("mode", "UNKNOWN"),
            p.get("position_uncertainty", 0)
        ])
        
        # In a real app we might have a flag if this is a raw GNSS measurement
        if "h_acc" in p:
            gnss_writer.writerow([
                ts,
                p.get("latitude", 0),
                p.get("longitude", 0),
                p.get("altitude", 0),
                p.get("speed", 0),
                p.get("course", 0),
                p.get("h_acc", 0),
                p.get("v_acc", 0)
            ])
            
        if "ai_speed_limit" in p:
            ai_writer.writerow([
                ts,
                p.get("ai_speed_limit", 0),
                p.get("ai_confidence", 0)
            ])

    # 4. Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Schema
        zf.writestr("schema_docs.txt", SCHEMA_DOCS)
        
        # CSVs
        zf.writestr("navigation.csv", nav_csv.getvalue())
        zf.writestr("gnss.csv", gnss_csv.getvalue())
        zf.writestr("ai_speed.csv", ai_csv.getvalue())
        
        # JSONs
        session_info = {
            "session_id": session_record.id,
            "start_time": session_record.start_time.isoformat() if session_record.start_time else None,
            "device_id": session_record.device_id
        }
        zf.writestr("session.json", json.dumps(session_info, indent=2))
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))
        zf.writestr("events.json", json.dumps(events, indent=2))
        zf.writestr("diagnostics.json", json.dumps(diagnostics, indent=2))
        
        # Benchmarks
        if experiments:
            exp_data = []
            for e in experiments:
                exp_data.append({
                    "id": e.id,
                    "configuration": e.configuration,
                    "results": e.results if not isinstance(e.results, str) else json.loads(e.results)
                })
            zf.writestr("benchmarks.json", json.dumps(exp_data, indent=2))

    zip_buffer.seek(0)
    return zip_buffer
