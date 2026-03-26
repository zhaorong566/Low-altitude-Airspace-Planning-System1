import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Drone(Base):
    __tablename__ = "drones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drone_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    model = Column(String(100), default="DJI Matrice 300")
    
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    current_alt = Column(Float, nullable=True)
    
    battery_level = Column(Float, default=100.0)
    max_payload = Column(Float, default=2.5)
    max_speed = Column(Float, default=15.0)
    max_altitude = Column(Float, default=120.0)
    
    is_available = Column(Boolean, default=True)
    current_task_id = Column(String(100), nullable=True)
    
    metadata_ = Column("metadata", JSON, default=dict)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
