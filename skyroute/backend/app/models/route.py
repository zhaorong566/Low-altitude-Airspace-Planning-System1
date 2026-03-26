import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("flight_tasks.id"), nullable=False)
    
    waypoints = Column(JSON, nullable=False)
    total_distance = Column(Float, default=0.0)
    total_duration = Column(Float, default=0.0)
    
    min_altitude = Column(Float, default=30.0)
    max_altitude = Column(Float, default=120.0)
    avg_altitude = Column(Float, default=60.0)
    
    risk_score = Column(Float, default=0.0)
    noise_score = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)
    
    version = Column(Integer, default=1)
    is_active = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
