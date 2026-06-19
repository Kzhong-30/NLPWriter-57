from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.registration import RegistrationStatus
from app.schemas import RegistrationCreate, Registration as RegistrationSchema, RegistrationStatusUpdate
from app.services import (
    register_user_to_activity,
    get_user_registrations,
    get_activity_registrations,
    get_registration,
    update_registration_status,
    get_current_active_user,
    get_current_organizer,
    get_activity,
)

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.post("/", response_model=RegistrationSchema, status_code=status.HTTP_201_CREATED)
def create_registration(
    registration_in: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    activity = get_activity(db, activity_id=registration_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    registration = register_user_to_activity(
        db=db,
        activity_id=registration_in.activity_id,
        user_id=current_user.id,
        remark=registration_in.remark,
    )
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Maybe already registered or activity is full.",
        )
    return registration


@router.get("/my", response_model=List[RegistrationSchema])
def read_my_registrations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    registrations = get_user_registrations(db, user_id=current_user.id, skip=skip, limit=limit)
    return registrations


@router.get("/activity/{activity_id}", response_model=List[RegistrationSchema])
def read_activity_registrations(
    activity_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[RegistrationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    activity = get_activity(db, activity_id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    registrations = get_activity_registrations(db, activity_id=activity_id, skip=skip, limit=limit, status=status)
    return registrations


@router.get("/{registration_id}", response_model=RegistrationSchema)
def read_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    registration = get_registration(db, registration_id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    if registration.user_id != current_user.id and current_user.role not in [UserRole.ORGANIZER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return registration


@router.patch("/{registration_id}/status", response_model=RegistrationSchema)
def update_registration_status_endpoint(
    registration_id: int,
    status_update: RegistrationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    registration = get_registration(db, registration_id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    activity = get_activity(db, activity_id=registration.activity_id)
    if activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    registration = update_registration_status(
        db=db,
        registration_id=registration_id,
        status=status_update.status,
        review_remark=status_update.review_remark,
    )
    return registration
