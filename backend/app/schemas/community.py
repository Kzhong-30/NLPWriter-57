from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StoryBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    activity_id: Optional[int] = None
    cover_image: Optional[str] = Field(None, max_length=500)


class StoryCreate(StoryBase):
    pass


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    cover_image: Optional[str] = Field(None, max_length=500)
    is_approved: Optional[bool] = None
    is_featured: Optional[bool] = None


class StoryInDB(StoryBase):
    id: int
    author_id: int
    views: int = 0
    likes: int = 0
    is_featured: bool = False
    is_approved: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Story(StoryInDB):
    pass


class StoryWithDetails(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    activity_id: Optional[int] = None
    cover_image: Optional[str] = None
    views: int
    likes: int
    is_featured: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    activity_title: Optional[str] = None

    class Config:
        from_attributes = True


class StoryLike(BaseModel):
    story_id: int


class ActivityPhotoCreate(BaseModel):
    activity_id: int
    image_url: str = Field(..., max_length=500)
    description: Optional[str] = Field(None, max_length=500)


class ActivityPhotoInDB(BaseModel):
    id: int
    activity_id: int
    uploaded_by: Optional[int] = None
    image_url: str
    description: Optional[str] = None
    likes: int = 0
    is_approved: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityPhoto(ActivityPhotoInDB):
    pass
