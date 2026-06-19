from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.activity import ActivityStatus


class ActivityPhotoBase(BaseModel):
    image_url: str
    description: Optional[str] = None


class ActivityPhotoCreate(ActivityPhotoBase):
    pass


class ActivityPhoto(ActivityPhotoBase):
    id: int
    activity_id: int
    user_id: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str
    start_time: datetime
    end_time: datetime
    location: str = Field(..., max_length=300)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_participants: int = Field(..., ge=1)
    service_content: str
    requirements: Optional[str] = None
    contact_info: Optional[str] = Field(None, max_length=200)
    cover_image: Optional[str] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=300)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_participants: Optional[int] = Field(None, ge=1)
    service_content: Optional[str] = None
    requirements: Optional[str] = None
    contact_info: Optional[str] = Field(None, max_length=200)
    cover_image: Optional[str] = None
    qr_code: Optional[str] = None


class ActivityStatusUpdate(BaseModel):
    status: ActivityStatus


class ActivityInDBBase(ActivityBase):
    id: int
    current_participants: int = 0
    qr_code: Optional[str] = None
    status: ActivityStatus
    organizer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Activity(ActivityInDBBase):
    pass


class ActivityInDB(ActivityInDBBase):
    pass


class ActivityListItem(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    max_participants: int
    current_participants: int
    cover_image: Optional[str]
    status: ActivityStatus
    organizer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
