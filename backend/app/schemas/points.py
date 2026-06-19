from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.points import TransactionType


class PointTransactionBase(BaseModel):
    type: TransactionType
    points: int
    description: str = Field(..., max_length=500)
    activity_id: Optional[int] = None
    reward_id: Optional[int] = None


class PointTransactionCreate(PointTransactionBase):
    user_id: int


class PointTransactionInDB(PointTransactionBase):
    id: int
    user_id: int
    balance_after: int
    created_at: datetime

    class Config:
        from_attributes = True


class PointTransaction(PointTransactionInDB):
    pass


class RewardBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    points_required: int
    stock: int = 0
    image: Optional[str] = Field(None, max_length=500)


class RewardCreate(RewardBase):
    pass


class RewardUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    points_required: Optional[int] = None
    stock: Optional[int] = None
    image: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class RewardInDB(RewardBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class Reward(RewardInDB):
    pass

class RewardExchangeBase(BaseModel):
    reward_id: int
    shipping_address: Optional[str] = Field(None, max_length=500)


class RewardExchangeCreate(RewardExchangeBase):
    pass


class RewardExchangeUpdate(BaseModel):
    status: str = Field(..., max_length=20)
    tracking_number: Optional[str] = Field(None, max_length=100)


class RewardExchangeInDB(RewardExchangeBase):
    id: int
    user_id: int
    points_spent: int
    status: str = "pending"
    tracking_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RewardExchange(RewardExchangeInDB):
    pass


class UserPointsResponse(BaseModel):
    user_id: int
    total_points: int
    total_hours: float
