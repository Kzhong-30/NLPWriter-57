from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class ActivityStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    location = Column(String(300), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    max_participants = Column(Integer, nullable=False)
    current_participants = Column(Integer, default=0)
    
    service_content = Column(Text, nullable=False)
    requirements = Column(Text)
    contact_info = Column(String(200))
    
    cover_image = Column(String(500))
    qr_code = Column(String(500))
    
    status = Column(String(50), default=ActivityStatus.DRAFT.value, nullable=False)
    
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    registrations = relationship("Registration", back_populates="activity")
    check_ins = relationship("CheckIn", back_populates="activity")
    photos = relationship("ActivityPhoto", back_populates="activity")
