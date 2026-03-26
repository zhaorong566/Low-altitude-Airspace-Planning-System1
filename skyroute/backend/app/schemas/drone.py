from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class DroneCreate(BaseModel):
    drone_id: str
    name: str
    model: str = "DJI Matrice 300"
    max_payload: float = 2.5
    max_speed: float = 15.0
    max_altitude: float = 120.0
    metadata: Optional[Dict[str, Any]] = None


class DroneUpdate(BaseModel):
    name: Optional[str] = None
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    current_alt: Optional[float] = None
    battery_level: Optional[float] = None
    is_available: Optional[bool] = None


class DroneResponse(BaseModel):
    id: UUID
    drone_id: str
    name: str
    model: str
    current_lat: Optional[float]
    current_lon: Optional[float]
    current_alt: Optional[float]
    battery_level: float
    max_payload: float
    max_speed: float
    max_altitude: float
    is_available: bool
    current_task_id: Optional[str]
    last_seen: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class DronePositionUpdate(BaseModel):
    drone_id: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    alt: float = Field(..., ge=0, le=500)
    heading: float = Field(default=0, ge=0, le=360)
    speed: float = Field(default=0, ge=0)
    battery_level: float = Field(default=100, ge=0, le=100)
    timestamp: Optional[float] = None
