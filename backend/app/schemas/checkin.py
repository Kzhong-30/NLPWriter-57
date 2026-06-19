from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.checkin import CheckInType, CheckInStatus


class CheckInCreate(BaseModel):
    activity_id: int
    check_in_type: CheckInType
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CheckOutUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CheckInInDB(BaseModel):
    id: int
    user_id: int
    activity_id: int
    check_in_type: CheckInType
    status: CheckInStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    check_in_latitude: Optional[float] = None
    check_in_longitude: Optional[float] = None
    check_out_latitude: Optional[float] = None
    check_out_longitude: Optional[float] = None
    service_hours: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


class CheckIn(CheckInInDB):
    pass

class CheckInWithDetails(BaseModel):
    id: int
    user_id: int
    activity_id: int
    check_in_type: CheckInType
    status: CheckInStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    service_hours: float = 0.0
    created_at: datetime
    user_full_name: Optional[str] = None
    activity_title: Optional[str] = None

    class Config:
        from_attributes = True
