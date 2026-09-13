from cloud.main import get_session_summary
from cloud.schemas import TelemetryPoint
from unittest.mock import MagicMock

def create_mock_db(session_id, points):
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_session.id = session_id
    
    mock_batch = MagicMock()
    # Ensure data are dicts as expected by all_points.extend(b.data) in cloud/main.py
    mock_batch.data = [p.dict() for p in points]
    
    mock_db.query().filter().first.return_value = mock_session
    mock_db.query().filter().order_by().all.return_value = [mock_batch]
    return mock_db

def test_event_timeline_generation():
    """Test that timeline events are generated in chronological order with correct fields."""
    
    # Simulate a session with GNSS loss, DR start, and GNSS recovery
    points = [
        # GNSS Good
        TelemetryPoint(timestamp=1000, latitude=10.0, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=5.0, v_acc=5.0, mode="GNSS_GOOD", map_match_confidence=0.1),
        TelemetryPoint(timestamp=2000, latitude=10.0001, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=5.0, v_acc=5.0, mode="GNSS_GOOD", map_match_confidence=0.1),
        
        # GNSS Loss, DR starts
        TelemetryPoint(timestamp=3000, latitude=10.0002, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=30.0, v_acc=5.0, mode="DEAD_RECKONING", map_match_confidence=0.1),
        TelemetryPoint(timestamp=4000, latitude=10.0003, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=35.0, v_acc=5.0, mode="DEAD_RECKONING", map_match_confidence=0.1),
        
        # Map matching
        TelemetryPoint(timestamp=5000, latitude=10.0004, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=40.0, v_acc=5.0, mode="DEAD_RECKONING", map_match_confidence=0.8),
        
        # GNSS Recovery
        TelemetryPoint(timestamp=6000, latitude=10.0005, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=8.0, v_acc=5.0, mode="GNSS_GOOD", map_match_confidence=0.9),
    ]
    
    mock_db = create_mock_db("test-session", points)
    summary = get_session_summary("test-session", mock_db)
    
    events = summary["events"]
    
    # Assert events exist
    assert len(events) > 0
    
    # Assert chronology
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps), "Events are not in chronological order"
    
    # Extract event types
    event_types = [e["type"] for e in events]
    
    assert "SESSION_STARTED" in event_types
    assert "GNSS_ACQUIRED" in event_types
    assert "GNSS_LOST" in event_types
    assert "DR_STARTED" in event_types
    assert "MAP_MATCHED" in event_types
    assert "GNSS_RECOVERED" in event_types
    assert "FUSION_COMPLETED" in event_types
    assert "SESSION_ENDED" in event_types
    
    # Verify fields
    dr_start = next(e for e in events if e["type"] == "DR_STARTED")
    assert dr_start["category"] == "DR"
    assert dr_start["severity"] == "WARNING"
    assert "speed" in dr_start["measurements"]
    
    map_match = next(e for e in events if e["type"] == "MAP_MATCHED")
    assert map_match["category"] == "Map"
    assert "confidence" in map_match["measurements"]

    gnss_lost = next(e for e in events if e["type"] == "GNSS_LOST")
    assert gnss_lost["category"] == "GNSS"
    assert gnss_lost["severity"] == "ERROR"
    assert "accuracy" in gnss_lost["measurements"]

def test_low_confidence_event():
    """Test that low confidence events are generated correctly."""
    points = [
        TelemetryPoint(timestamp=1000, latitude=10.0, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=5.0, v_acc=5.0, mode="GNSS_GOOD", map_match_confidence=0.1),
        TelemetryPoint(timestamp=2000, latitude=10.0001, longitude=20.0, altitude=100.0, speed=10.0, course=90.0, 
                       h_acc=25.0, v_acc=5.0, mode="GNSS_GOOD", map_match_confidence=0.1), # High uncertainty
    ]
    
    mock_db = create_mock_db("test-session-2", points)
    summary = get_session_summary("test-session-2", mock_db)
    events = summary["events"]
    
    low_conf = next((e for e in events if e["type"] == "LOW_CONFIDENCE"), None)
    assert low_conf is not None
    assert low_conf["category"] == "Errors"
    assert low_conf["severity"] == "WARNING"
