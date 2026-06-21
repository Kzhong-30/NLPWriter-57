from typing import List
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
    total: int
    draft: int
    published: int
    ongoing: int
    completed: int
    cancelled: int


class UserStats(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
    volunteers: int
    organizers: int
    admins: int
    total_service_hours: float
    avg_service_hours: float

class MonthlyStats(BaseModel):
    this_month_users: int
    last_month_users: int
    this_month_activities: int
    last_month_activities: int
    this_month_registrations: int
    last_month_registrations: int
    this_month_hours: float
    last_month_hours: float

class TrendData(BaseModel):
    labels: List[str]
    new_users: List[int]
    new_activities: List[int]
    service_hours: List[float]


class StatsResponse(BaseModel):
    dashboard: DashboardStats
    activities: ActivityStats
    users: UserStats
    monthly: MonthlyStats
