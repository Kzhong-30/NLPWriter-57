from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.community import Story, ActivityPhoto
from app.schemas import StoryCreate, StoryUpdate, Story as StorySchema, StoryWithDetails, ActivityPhotoCreate, ActivityPhoto as ActivityPhotoSchema
from app.services import (
    get_current_active_user,
    get_current_organizer,
    get_activity,
)

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/stories", response_model=List[StoryWithDetails])
def read_stories(
    skip: int = 0,
    limit: int = 100,
    activity_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> Any:
    query = db.query(Story).filter(Story.is_approved == True)
    if activity_id:
        query = query.filter(Story.activity_id == activity_id)
    return query.order_by(Story.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stories/my", response_model=List[StoryWithDetails])
def read_my_stories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    stories = db.query(Story).filter(
        Story.user_id == current_user.id,
    ).order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
    return stories


@router.get("/stories/{story_id}", response_model=StoryWithDetails)
def read_story(
    story_id: int,
    db: Session = Depends(get_db),
) -> Any:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    return story


@router.post("/stories", response_model=StorySchema, status_code=status.HTTP_201_CREATED)
def create_story(
    story_in: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if story_in.activity_id:
        activity = get_activity(db, activity_id=story_in.activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
    db_story = Story(
        user_id=current_user.id,
        activity_id=story_in.activity_id,
        title=story_in.title,
        content=story_in.content,
        images=story_in.images,
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


@router.put("/stories/{story_id}", response_model=StorySchema)
def update_story(
    story_id: int,
    story_in: StoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    if story.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    for key, value in story_in.model_dump(exclude_unset=True).items():
        setattr(story, key, value)
    db.commit()
    db.refresh(story)
    return story


@router.patch("/stories/{story_id}/approve", response_model=StorySchema)
def approve_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    story.is_approved = True
    db.commit()
    db.refresh(story)
    return story


@router.delete("/stories/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    if story.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    db.delete(story)
    db.commit()


@router.get("/photos", response_model=List[ActivityPhotoSchema])
def read_photos(
    skip: int = 0,
    limit: int = 100,
    activity_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> Any:
    query = db.query(ActivityPhoto).filter(ActivityPhoto.is_approved == True)
    if activity_id:
        query = query.filter(ActivityPhoto.activity_id == activity_id)
    return query.order_by(ActivityPhoto.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/photos", response_model=ActivityPhotoSchema, status_code=status.HTTP_201_CREATED)
def upload_photo(
    photo_in: ActivityPhotoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    activity = get_activity(db, activity_id=photo_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    db_photo = ActivityPhoto(
        activity_id=photo_in.activity_id,
        user_id=current_user.id,
        image_url=photo_in.image_url,
        description=photo_in.description,
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.patch("/photos/{photo_id}/approve", response_model=ActivityPhotoSchema)
def approve_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    photo = db.query(ActivityPhoto).filter(ActivityPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    photo.is_approved = True
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    photo = db.query(ActivityPhoto).filter(ActivityPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    if photo.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    db.delete(photo)
    db.commit()
