from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.activity import Activity, ActivityStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.checkin import CheckIn
from datetime import datetime


def get_activity(db: Session, activity_id: int) -> Optional[Activity]:
    return db.query(Activity).filter(Activity.id == activity_id).first()


def get_activities(db: Session, skip: int = 0, limit: int = 100, status: Optional[ActivityStatus] = None, organizer_id: Optional[int] = None) -> List[Activity]:
    query = db.query(Activity)
    if status:
        query = query.filter(Activity.status == status)
    if organizer_id:
        query = query.filter(Activity.organizer_id == organizer_id)
    return query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()


def create_activity(db: Session, title: str, description: str, start_time: datetime, end_time: datetime, location: str, max_participants: int, service_content: str, organizer_id: int, latitude: Optional[float] = None, longitude: Optional[float] = None, requirements: Optional[str] = None, contact_info: Optional[str] = None, cover_image: Optional[str] = None) -> Activity:
    db_activity = Activity(
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        location=location,
        latitude=latitude,
        longitude=longitude,
        max_participants=max_participants,
        service_content=service_content,
        requirements=requirements,
        contact_info=contact_info,
        cover_image=cover_image,
        organizer_id=organizer_id,
        status=ActivityStatus.DRAFT,
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity(db: Session, activity_id: int, **kwargs) -> Optional[Activity]:
    db_activity = get_activity(db, activity_id)
    if not db_activity:
        return None
    for key, value in kwargs.items():
        if hasattr(db_activity, key) and value is not None:
            setattr(db_activity, key, value)
    db_activity.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity_status(db: Session, activity_id: int, status: ActivityStatus) -> Optional[Activity]:
    return update_activity(db, activity_id, status=status)


def delete_activity(db: Session, activity_id: int) -> bool:
    db_activity = get_activity(db, activity_id)
    if not db_activity:
        return False
    db.delete(db_activity)
    db.commit()
    return True


def register_user_to_activity(db: Session, activity_id: int, user_id: int, remark: Optional[str] = None) -> Optional[Registration]:
    activity = get_activity(db, activity_id)
    if not activity or activity.current_participants >= activity.max_participants:
        return None
    existing_reg = db.query(Registration).filter(Registration.activity_id == activity_id, Registration.user_id == user_id).first()
    if existing_reg:
        return None
    db_registration = Registration(
        activity_id=activity_id,
        user_id=user_id,
        remark=remark,
        status=RegistrationStatus.PENDING,
    )
    activity.current_participants += 1
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration


def get_user_registrations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Registration]:
    return db.query(Registration).filter(Registration.user_id == user_id).order_by(Registration.created_at.desc()).offset(skip).limit(limit).all()


def get_activity_registrations(db: Session, activity_id: int, skip: int = 0, limit: int = 100, status: Optional[RegistrationStatus] = None) -> List[Registration]:
    query = db.query(Registration).filter(Registration.activity_id == activity_id)
    if status:
        query = query.filter(Registration.status == status)
    return query.order_by(Registration.created_at.desc()).offset(skip).limit(limit).all()


def get_registration(db: Session, registration_id: int) -> Optional[Registration]:
    return db.query(Registration).filter(Registration.id == registration_id).first()


def update_registration_status(db: Session, registration_id: int, status: RegistrationStatus, review_remark: Optional[str] = None) -> Optional[Registration]:
    db_reg = get_registration(db, registration_id)
    if not db_reg:
        return None
    db_reg.status = status
    db_reg.review_remark = review_remark
    db_reg.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_reg)
    return db_reg


def create_check_in(db: Session, activity_id: int, user_id: int, check_in_type: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Optional[CheckIn]:
    from app.models.checkin import CheckInStatus
    activity = get_activity(db, activity_id)
    if not activity:
        return None
    registration = db.query(Registration).filter(Registration.activity_id == activity_id, Registration.user_id == user_id, Registration.status == RegistrationStatus.APPROVED).first()
    if not registration:
        return None
    existing_checkin = db.query(CheckIn).filter(CheckIn.activity_id == activity_id, CheckIn.user_id == user_id, CheckIn.status == CheckInStatus.CHECKED_IN).first()
    if existing_checkin:
        return None
    db_checkin = CheckIn(
        activity_id=activity_id,
        user_id=user_id,
        check_in_type=check_in_type,
        check_in_latitude=latitude,
        check_in_longitude=longitude,
        status=CheckInStatus.CHECKED_IN,
        check_in_time=datetime.utcnow(),
    )
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


def create_check_out(db: Session, checkin_id: int, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Optional[CheckIn]:
    from app.models.checkin import CheckInStatus
    from app.services.user_service import add_user_hours
    db_checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not db_checkin or db_checkin.status != CheckInStatus.CHECKED_IN:
        return None
    db_checkin.status = CheckInStatus.CHECKED_OUT
    db_checkin.check_out_time = datetime.utcnow()
    db_checkin.check_out_latitude = latitude
    db_checkin.check_out_longitude = longitude
    if db_checkin.check_in_time and db_checkin.check_out_time:
        delta = db_checkin.check_out_time - db_checkin.check_in_time
        db_checkin.service_hours = round(delta.total_seconds() / 3600, 2)
        add_user_hours(db, db_checkin.user_id, db_checkin.service_hours)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


def get_user_check_ins(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[CheckIn]:
    return db.query(CheckIn).filter(CheckIn.user_id == user_id).order_by(CheckIn.created_at.desc()).offset(skip).limit(limit).all()


def get_activity_check_ins(db: Session, activity_id: int, skip: int = 0, limit: int = 100) -> List[CheckIn]:
    return db.query(CheckIn).filter(CheckIn.activity_id == activity_id).order_by(CheckIn.created_at.desc()).offset(skip).limit(limit).all()
