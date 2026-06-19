from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    certificate_number = Column(String(50), unique=True, nullable=False)
    
    title = Column(String(200), nullable=False)
    activity_name = Column(String(200))
    total_hours = Column(Float, nullable=False)
    
    issued_date = Column(DateTime, default=datetime.utcnow)
    issued_by = Column(Integer, ForeignKey("users.id"))
    
    certificate_url = Column(String(500))
    qr_code = Column(String(500))
    
    is_verified = Column(Boolean, default=True)
    
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="certificates", foreign_keys=[user_id])
