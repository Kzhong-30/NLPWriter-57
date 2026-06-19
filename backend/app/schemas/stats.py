from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_users: int
    total_activities: int
    total_registrations: int
    total_check_ins: int
    total_certificates: int
    total_service_hours: float
    total_points_earned: int
    pending_registrations: int


class ActivityStats(BaseModel):
    activity_id: int
    activity_title: str
    total_registrations: int
    approved_registrations: int
    total_check_ins: int
    total_service_hours: float
    avg_rating: Optional[float] = None


class UserStats(BaseModel):
    user_id: int
    user_name: str
    total_activities: int
    total_check_ins: int
    total_service_hours: float
    total_points: int
    total_certificates: int


class MonthlyStats(BaseModel):
    month: str
    year: int
    new_users: int
    new_activities: int
    total_registrations: int
    total_service_hours: float


class TrendData(BaseModel):
    labels: list
    values: list


class StatsResponse(BaseModel):
    dashboard: DashboardStats
    activities: list
    recent_users: list
    monthly_trend: TrendData
    category_distribution: Dict[str, int]
