from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.activity import ActivityStatus
from app.schemas import ActivityCreate, ActivityUpdate, Activity as ActivitySchema, ActivityListItem
from app.services import (
    get_activity,
    get_activities,
    create_activity,
    update_activity,
    update_activity_status,
    delete_activity,
    get_current_organizer,
    get_current_active_user,
)

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=List[ActivityListItem])
def read_activities(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ActivityStatus] = None,
    db: Session = Depends(get_db),
) -> Any:
    activities = get_activities(db, skip=skip, limit=limit, status=status)
    return activities


@router.get("/{activity_id}", response_model=ActivitySchema)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db),
) -> Any:
    db_activity = get_activity(db, activity_id=activity_id)
    if not db_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    return db_activity


@router.post("/", response_model=ActivitySchema, status_code=status.HTTP_201_CREATED)
def create_activity_endpoint(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    activity = create_activity(
        db=db,
        title=activity_in.title,
        description=activity_in.description,
        start_time=activity_in.start_time,
        end_time=activity_in.end_time,
        location=activity_in.location,
        max_participants=activity_in.max_participants,
        service_content=activity_in.service_content,
        organizer_id=current_user.id,
        latitude=activity_in.latitude,
        longitude=activity_in.longitude,
        requirements=activity_in.requirements,
        contact_info=activity_in.contact_info,
        cover_image=activity_in.cover_image,
    )
    return activity


@router.put("/{activity_id}", response_model=ActivitySchema)
def update_activity_endpoint(
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    db_activity = get_activity(db, activity_id=activity_id)
    if not db_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if db_activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    activity = update_activity(db, activity_id=activity_id, **activity_in.model_dump(exclude_unset=True))
    return activity


@router.patch("/{activity_id}/status", response_model=ActivitySchema)
def update_activity_status_endpoint(
    activity_id: int,
    status: ActivityStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    db_activity = get_activity(db, activity_id=activity_id)
    if not db_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if db_activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    activity = update_activity_status(db, activity_id=activity_id, status=status)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity_endpoint(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> None:
    db_activity = get_activity(db, activity_id=activity_id)
    if not db_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if db_activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    delete_activity(db, activity_id=activity_id)
