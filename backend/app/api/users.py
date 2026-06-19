from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas import UserUpdate, User as UserSchema, UserStatusUpdate, UserRoleUpdate
from app.services import (
    get_user,
    get_users,
    update_user,
    update_user_status,
    update_user_role,
    delete_user,
    get_current_active_user,
    get_current_admin,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    return current_user


@router.get("/", response_model=List[UserSchema])
def read_users(
    skip: int = 0,
    limit: int = 100,
    role: UserRole = None,
    status: UserStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    users = get_users(db, skip=skip, limit=limit, role=role, status=status)
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return db_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    user = update_user(db, user_id=current_user.id, **user_in.model_dump(exclude_unset=True))
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user_by_id(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = update_user(db, user_id=user_id, **user_in.model_dump(exclude_unset=True))
    return user


@router.patch("/{user_id}/status", response_model=UserSchema)
def update_user_status_endpoint(
    user_id: int,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = update_user_status(db, user_id=user_id, status=status_update.status)
    return user


@router.patch("/{user_id}/role", response_model=UserSchema)
def update_user_role_endpoint(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = update_user_role(db, user_id=user_id, role=role_update.role)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> None:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    delete_user(db, user_id=user_id)
