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

Base.metadata.create_all(bind=engine)
