from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.activities import router as activities_router
from app.api.registrations import router as registrations_router
from app.api.checkins import router as checkins_router
from app.api.certificates import router as certificates_router
from app.api.points import router as points_router
from app.api.stats import router as stats_router
from app.api.community import router as community_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(activities_router)
api_router.include_router(registrations_router)
api_router.include_router(checkins_router)
api_router.include_router(certificates_router)
api_router.include_router(points_router)
api_router.include_router(stats_router)
api_router.include_router(community_router)

__all__ = ["api_router"]
