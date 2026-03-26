import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlightTask(Base):
    __tablename__ = "flight_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    drone_id = Column(String(100), nullable=False)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    origin_alt = Column(Float, default=50.0)
    
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)
    dest_alt = Column(Float, default=50.0)
    
    planned_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    route_data = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    
    priority = Column(String(20), default="normal")
    task_type = Column(String(50), default="delivery")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
