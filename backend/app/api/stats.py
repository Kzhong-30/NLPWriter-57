from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.activity import Activity, ActivityStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.checkin import CheckIn, CheckInStatus
from app.models.certificate import Certificate
from app.models.points import PointTransaction, TransactionType
# from app.models.community import Story, ActivityPhoto  # 暂时注释，未在统计接口中使用
from app.schemas.stats import DashboardStats, ActivityStats, UserStats, StatsResponse, MonthlyStats, TrendData
from app.services import get_current_admin

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_activities = db.query(func.count(Activity.id)).scalar() or 0
    total_registrations = db.query(func.count(Registration.id)).scalar() or 0
    total_check_ins = db.query(func.count(CheckIn.id)).scalar() or 0
    total_certificates = db.query(func.count(Certificate.id)).scalar() or 0
    total_hours = db.query(func.sum(CheckIn.service_hours)).scalar() or 0
    total_points = db.query(func.sum(PointTransaction.points)).filter(
        PointTransaction.type == TransactionType.EARN.value
    ).scalar() or 0
    pending_registrations = db.query(func.count(Registration.id)).filter(Registration.status == RegistrationStatus.PENDING).scalar() or 0
    return DashboardStats(
        total_users=total_users,
        total_activities=total_activities,
        total_registrations=total_registrations,
        total_check_ins=total_check_ins,
        total_certificates=total_certificates,
        total_service_hours=float(total_hours),
        total_points_earned=int(total_points),
        pending_registrations=pending_registrations,
    )


@router.get("/activities", response_model=ActivityStats)
def get_activity_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    total = db.query(func.count(Activity.id)).scalar() or 0
    draft = db.query(func.count(Activity.id)).filter(Activity.status == ActivityStatus.DRAFT).scalar() or 0
    published = db.query(func.count(Activity.id)).filter(Activity.status == ActivityStatus.PUBLISHED).scalar() or 0
    ongoing = db.query(func.count(Activity.id)).filter(Activity.status == ActivityStatus.ONGOING).scalar() or 0
    completed = db.query(func.count(Activity.id)).filter(Activity.status == ActivityStatus.COMPLETED).scalar() or 0
    cancelled = db.query(func.count(Activity.id)).filter(Activity.status == ActivityStatus.CANCELLED).scalar() or 0
    return ActivityStats(
        total=total,
        draft=draft,
        published=published,
        ongoing=ongoing,
        completed=completed,
        cancelled=cancelled,
    )


@router.get("/users", response_model=UserStats)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    total = db.query(func.count(User.id)).scalar() or 0
    pending = db.query(func.count(User.id)).filter(User.status == UserStatus.PENDING).scalar() or 0
    approved = db.query(func.count(User.id)).filter(User.status == UserStatus.APPROVED).scalar() or 0
    rejected = db.query(func.count(User.id)).filter(User.status == UserStatus.REJECTED).scalar() or 0
    volunteers = db.query(func.count(User.id)).filter(User.role == UserRole.VOLUNTEER).scalar() or 0
    organizers = db.query(func.count(User.id)).filter(User.role == UserRole.ORGANIZER).scalar() or 0
    admins = db.query(func.count(User.id)).filter(User.role == UserRole.ADMIN).scalar() or 0
    total_hours = db.query(func.sum(CheckIn.service_hours)).scalar() or 0
    avg_hours = float(total_hours) / approved if approved > 0 else 0
    return UserStats(
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        volunteers=volunteers,
        organizers=organizers,
        admins=admins,
        total_service_hours=float(total_hours),
        avg_service_hours=round(avg_hours, 2),
    )


@router.get("/monthly", response_model=MonthlyStats)
def get_monthly_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    now = datetime.utcnow()
    this_month_start = datetime(now.year, now.month, 1)
    last_month_start = datetime(now.year, now.month - 1, 1) if now.month > 1 else datetime(now.year - 1, 12, 1)
    next_month_start = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
    this_month_users = db.query(func.count(User.id)).filter(User.created_at >= this_month_start, User.created_at < next_month_start).scalar() or 0
    last_month_users = db.query(func.count(User.id)).filter(User.created_at >= last_month_start, User.created_at < this_month_start).scalar() or 0
    this_month_activities = db.query(func.count(Activity.id)).filter(Activity.created_at >= this_month_start, Activity.created_at < next_month_start).scalar() or 0
    last_month_activities = db.query(func.count(Activity.id)).filter(Activity.created_at >= last_month_start, Activity.created_at < this_month_start).scalar() or 0
    this_month_registrations = db.query(func.count(Registration.id)).filter(Registration.created_at >= this_month_start, Registration.created_at < next_month_start).scalar() or 0
    last_month_registrations = db.query(func.count(Registration.id)).filter(Registration.created_at >= last_month_start, Registration.created_at < this_month_start).scalar() or 0
    this_month_hours = db.query(func.sum(CheckIn.service_hours)).filter(CheckIn.created_at >= this_month_start, CheckIn.created_at < next_month_start).scalar() or 0
    last_month_hours = db.query(func.sum(CheckIn.service_hours)).filter(CheckIn.created_at >= last_month_start, CheckIn.created_at < this_month_start).scalar() or 0
    return MonthlyStats(
        this_month_users=this_month_users,
        last_month_users=last_month_users,
        this_month_activities=this_month_activities,
        last_month_activities=last_month_activities,
        this_month_registrations=this_month_registrations,
        last_month_registrations=last_month_registrations,
        this_month_hours=float(this_month_hours),
        last_month_hours=float(last_month_hours),
    )


@router.get("/trend/{months}", response_model=TrendData)
def get_trend_data(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    if months < 1 or months > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Months must be between 1 and 24",
        )
    labels = []
    user_data = []
    activity_data = []
    hour_data = []
    now = datetime.utcnow()
    for i in range(months - 1, -1, -1):
        year = now.year
        month = now.month - i
        if month <= 0:
            month += 12
            year -= 1
        month_start = datetime(year, month, 1)
        if month < 12:
            next_month_start = datetime(year, month + 1, 1)
        else:
            next_month_start = datetime(year + 1, 1, 1)
        labels.append(f"{year}年{month}月")
        user_count = db.query(func.count(User.id)).filter(User.created_at >= month_start, User.created_at < next_month_start).scalar() or 0
        user_data.append(user_count)
        activity_count = db.query(func.count(Activity.id)).filter(Activity.created_at >= month_start, Activity.created_at < next_month_start).scalar() or 0
        activity_data.append(activity_count)
        hours = db.query(func.sum(CheckIn.service_hours)).filter(CheckIn.created_at >= month_start, CheckIn.created_at < next_month_start).scalar() or 0
        hour_data.append(float(hours))
    return TrendData(
        labels=labels,
        new_users=user_data,
        new_activities=activity_data,
        service_hours=hour_data,
    )


@router.get("/all", response_model=StatsResponse)
def get_all_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    return StatsResponse(
        dashboard=get_dashboard_stats(db, current_user),
        activities=get_activity_stats(db, current_user),
        users=get_user_stats(db, current_user),
        monthly=get_monthly_stats(db, current_user),
    )
