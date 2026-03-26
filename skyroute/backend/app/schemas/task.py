from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"


class TaskType(str, enum.Enum):
    DELIVERY = "delivery"
    INSPECTION = "inspection"
    EMERGENCY = "emergency"
    SURVEY = "survey"
    PATROL = "patrol"


class WaypointSchema(BaseModel):
    lat: float
    lon: float
    alt: float
    speed: Optional[float] = 10.0
    timestamp: Optional[float] = None


class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    drone_id: str
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lon: float = Field(..., ge=-180, le=180)
    origin_alt: float = Field(default=50.0, ge=0, le=500)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lon: float = Field(..., ge=-180, le=180)
    dest_alt: float = Field(default=50.0, ge=0, le=500)
    planned_start: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.NORMAL
    task_type: TaskType = TaskType.DELIVERY
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    planned_start: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: UUID
    name: str
    drone_id: str
    status: TaskStatus
    origin_lat: float
    origin_lon: float
    origin_alt: float
    dest_lat: float
    dest_lon: float
    dest_alt: float
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    route_data: Optional[Dict[str, Any]]
    priority: str
    task_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
