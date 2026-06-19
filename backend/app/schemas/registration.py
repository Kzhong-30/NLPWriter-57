from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.registration import RegistrationStatus


class RegistrationBase(BaseModel):
    activity_id: int
    remark: Optional[str] = None


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationUpdate(BaseModel):
    remark: Optional[str] = None
    status: Optional[RegistrationStatus] = None


class RegistrationStatusUpdate(BaseModel):
    status: RegistrationStatus
    review_remark: Optional[str] = None


class RegistrationInDBBase(RegistrationBase):
    id: int
    user_id: int
    status: RegistrationStatus
    review_remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Registration(RegistrationInDBBase):
    pass


class RegistrationInDB(RegistrationInDBBase):
    pass


class RegistrationWithDetails(RegistrationInDBBase):
    user: Optional[object] = None
    activity: Optional[object] = None
