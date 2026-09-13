from sqlalchemy import create_engine, Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./navigators_cloud.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SessionRecord(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    device_id = Column(String, index=True)
    metadata_json = Column(JSON, nullable=True)

class TelemetryBatch(Base):
    __tablename__ = "telemetry_batches"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    timestamp_received = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON) # Stores list of points to save space/complexity for now

class VehicleProfile(Base):
    __tablename__ = "vehicle_profiles"
    id = Column(String, primary_key=True, index=True)
    device_id = Column(String, index=True)
    name = Column(String)
    vehicle_type = Column(String)
    phone_mounting = Column(String)
    is_calibrated = Column(Integer, default=0) # SQLite doesn't have native boolean
    external_imu = Column(Integer, default=0)
    alignment_params = Column(JSON, nullable=True)
    calibration_params = Column(JSON, nullable=True)
    nav_prefs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExperimentRecord(Base):
    __tablename__ = "experiments"
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(Float)
    device = Column(String)
    session_id = Column(String, index=True)
    model_version = Column(String)
    map_version = Column(String)
    configuration = Column(String)
    outage_scenario = Column(String)
    results = Column(JSON) # Store metrics (position_error, drift, etc.)
    
Base.metadata.create_all(bind=engine)
