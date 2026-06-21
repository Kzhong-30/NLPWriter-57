from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"
    ADMIN = "admin"

class UserStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    avatar = Column(String(500))
    
    role = Column(String(50), default=UserRole.VOLUNTEER.value, nullable=False)
    status = Column(String(50), default=UserStatus.PENDING.value, nullable=False)
    
    id_card = Column(String(20))
    skills = Column(String(500))
    experience = Column(Text)
    organization = Column(String(200))
    
    total_hours = Column(Float, default=0.0)
    total_points = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    registrations = relationship("Registration", back_populates="user")
    check_ins = relationship("CheckIn", back_populates="user")
    certificates = relationship("Certificate", back_populates="user", foreign_keys="Certificate.user_id")
    point_transactions = relationship("PointTransaction", back_populates="user")
    stories = relationship("Story", back_populates="author")
