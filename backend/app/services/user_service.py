from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, verify_password
from datetime import datetime


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, role: Optional[UserRole] = None, status: Optional[UserStatus] = None) -> List[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, username: str, email: str, password: str, full_name: str, phone: Optional[str] = None, role: UserRole = UserRole.VOLUNTEER) -> User:
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        phone=phone,
        role=role,
        status=UserStatus.PENDING if role == UserRole.VOLUNTEER else UserStatus.APPROVED,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    if "password" in kwargs:
        kwargs["hashed_password"] = get_password_hash(kwargs.pop("password"))
    for key, value in kwargs.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_status(db: Session, user_id: int, status: UserStatus) -> Optional[User]:
    return update_user(db, user_id, status=status)


def update_user_role(db: Session, user_id: int, role: UserRole) -> Optional[User]:
    return update_user(db, user_id, role=role)


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def add_user_points(db: Session, user_id: int, points: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db_user.total_points += points
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def add_user_hours(db: Session, user_id: int, hours: float) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db_user.total_hours += hours
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user
