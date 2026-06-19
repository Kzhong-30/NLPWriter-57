from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CertificateBase(BaseModel):
    title: str = Field(..., max_length=200)
    activity_name: Optional[str] = Field(None, max_length=200)
    total_hours: float
    description: Optional[str] = None


class CertificateCreate(CertificateBase):
    user_id: int


class CertificateGenerate(BaseModel):
    user_id: int
    activity_id: Optional[int] = None
    title: str = Field(..., max_length=200)
    description: Optional[str] = None


class CertificateInDB(CertificateBase):
    id: int
    user_id: int
    certificate_number: str
    issued_date: datetime
    issued_by: Optional[int] = None
    certificate_url: Optional[str] = Field(None, max_length=500)
    qr_code: Optional[str] = Field(None, max_length=500)
    is_verified: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class Certificate(CertificateInDB):
    pass

class CertificateWithUser(BaseModel):
    id: int
    user_id: int
    certificate_number: str
    title: str
    activity_name: Optional[str] = None
    total_hours: float
    issued_date: datetime
    certificate_url: Optional[str] = None
    qr_code: Optional[str] = None
    is_verified: bool
    description: Optional[str] = None
    created_at: datetime
    user_full_name: Optional[str] = None

    class Config:
        from_attributes = True
