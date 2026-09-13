from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TelemetryPoint(BaseModel):
    timestamp: float = Field(..., description="UNIX timestamp of the measurement")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude: float = Field(...)
    speed: float = Field(..., ge=0.0)
    course: float = Field(...)
    h_acc: float = Field(..., ge=0.0)
    v_acc: float = Field(..., ge=0.0)
    mode: str = Field(...)
    map_status: Optional[str] = None
    map_match_confidence: Optional[float] = None
    
    class Config:
        extra = "allow" # allow extra fields like raw sensor data if needed

class TelemetryBatchPayload(BaseModel):
    batch: List[TelemetryPoint] = Field(..., max_items=1000)

class ExperimentResults(BaseModel):
    position_error: float
    drift_percent: float
    speed_rmse: float
    heading_error: float
    speed_mae: Optional[float] = None
    max_error: Optional[float] = None
    inference_latency_ms: Optional[float] = None
    model_size_mb: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    dataset: Optional[str] = None
    preprocessing_version: Optional[str] = None

class ExperimentRecord(BaseModel):
    id: str
    timestamp: float
    device: str
    session_id: str
    model_version: str
    map_version: str
    configuration: str
    outage_scenario: str
    results: ExperimentResults

class VehicleProfileBase(BaseModel):
    name: str
    vehicle_type: str
    phone_mounting: str
    external_imu: bool = False
    nav_prefs: Optional[dict] = None

class VehicleProfileCreate(VehicleProfileBase):
    pass

class VehicleProfileUpdate(BaseModel):
    name: Optional[str] = None
    vehicle_type: Optional[str] = None
    phone_mounting: Optional[str] = None
    external_imu: Optional[bool] = None
    is_calibrated: Optional[bool] = None
    alignment_params: Optional[dict] = None
    calibration_params: Optional[dict] = None
    nav_prefs: Optional[dict] = None

class VehicleProfileResponse(VehicleProfileBase):
    id: str
    device_id: str
    is_calibrated: bool
    alignment_params: Optional[dict] = None
    calibration_params: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FeedbackReportCreate(BaseModel):
    category: str
    description: str
    severity: str
    session_id: Optional[str] = None
    technical_context: Optional[dict] = None
    rating: Optional[str] = None

class FeedbackStatusUpdate(BaseModel):
    status: str

class FeedbackReportResponse(BaseModel):
    id: str
    device_id: str
    category: str
    description: str
    severity: str
    status: str
    session_id: Optional[str] = None
    technical_context: Optional[dict] = None
    rating: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
