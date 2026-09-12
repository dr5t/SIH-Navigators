from pydantic import BaseModel, Field
from typing import List, Optional

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
