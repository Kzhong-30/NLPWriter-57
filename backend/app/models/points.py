from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class TransactionType(str, enum.Enum):
    EARN = "earn"
    AWARD = "award"
    EXCHANGE = "exchange"
    SPEND = "spend"


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    type = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    
    description = Column(String(500), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    reward_id = Column(Integer, ForeignKey("rewards.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="point_transactions")


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    points_required = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RewardExchange(Base):
    __tablename__ = "reward_exchanges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    
    points_spent = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reward = relationship("Reward")
