from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class CheckInType(str, enum.Enum):
    QR_CODE = "qr_code"
    GPS = "gps"
    LOCATION = "location"


class CheckInStatus(str, enum.Enum):
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"


class CheckIn(Base):
    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    check_in_type = Column(String(50), nullable=False)
    status = Column(String(50), default=CheckInStatus.CHECKED_IN.value, nullable=False)
    
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    check_in_latitude = Column(Float)
    check_in_longitude = Column(Float)
    check_out_latitude = Column(Float)
    check_out_longitude = Column(Float)
    
    service_hours = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="check_ins")
    activity = relationship("Activity", back_populates="check_ins")
