from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole, UserStatus


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = None
    id_card: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    organization: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: Optional[UserRole] = UserRole.VOLUNTEER


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = None
    id_card: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    organization: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserInDBBase(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    total_hours: float = 0.0
    total_points: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class UserListItem(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    total_hours: float
    total_points: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
