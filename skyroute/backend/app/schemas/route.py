from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class WaypointOut(BaseModel):
    lat: float
    lon: float
    alt: float
    speed: float = 10.0
    timestamp: Optional[float] = None


class RouteCreate(BaseModel):
    task_id: UUID
    waypoints: List[WaypointOut]


class RouteResponse(BaseModel):
    id: UUID
    task_id: UUID
    waypoints: List[WaypointOut]
    total_distance: float
    total_duration: float
    min_altitude: float
    max_altitude: float
    avg_altitude: float
    risk_score: float
    noise_score: float
    efficiency_score: float
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlanningRequest(BaseModel):
    task_id: UUID
    avoid_no_fly: bool = True
    avoid_noise: bool = True
    optimize_altitude: bool = True
    max_altitude: float = Field(default=120.0, ge=10, le=500)
    preferred_speed: float = Field(default=10.0, ge=1, le=30)
