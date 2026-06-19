from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.checkin import CheckInType, CheckInStatus
from app.schemas import CheckInCreate, CheckOutUpdate, CheckIn as CheckInSchema, CheckInWithDetails
from app.utils.geo_utils import is_within_radius
from app.services import (
    create_check_in,
    create_check_out,
    get_user_check_ins,
    get_activity_check_ins,
    get_current_active_user,
    get_current_organizer,
    get_activity,
)

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post("/check-in", response_model=CheckInSchema, status_code=status.HTTP_201_CREATED)
def check_in(
    checkin_in: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    activity = get_activity(db, activity_id=checkin_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if checkin_in.check_in_type == CheckInType.LOCATION and activity.latitude and activity.longitude:
        if not is_within_radius(
            checkin_in.latitude,
            checkin_in.longitude,
            activity.latitude,
            activity.longitude,
            radius_meters=100.0,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not within activity location range",
            )
    checkin = create_check_in(
        db=db,
        activity_id=checkin_in.activity_id,
        user_id=current_user.id,
        check_in_type=checkin_in.check_in_type,
        latitude=checkin_in.latitude,
        longitude=checkin_in.longitude,
    )
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in failed. Already checked in or not registered.",
        )
    return checkin


@router.post("/check-out/{checkin_id}", response_model=CheckInSchema)
def check_out(
    checkin_id: int,
    checkout_in: CheckOutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    checkin = create_check_out(
        db=db,
        checkin_id=checkin_id,
        latitude=checkout_in.latitude,
        longitude=checkout_in.longitude,
    )
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out failed. Check-in not found or already checked out.",
        )
    if checkin.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return checkin


@router.get("/my", response_model=List[CheckInWithDetails])
def read_my_check_ins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    checkins = get_user_check_ins(db, user_id=current_user.id, skip=skip, limit=limit)
    return checkins


@router.get("/activity/{activity_id}", response_model=List[CheckInWithDetails])
def read_activity_check_ins(
    activity_id: int,
    skip: int = 0,
    limit: int = 100,
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
    checkins = get_activity_check_ins(db, activity_id=activity_id, skip=skip, limit=limit)
    return checkins
