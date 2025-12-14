"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import health, profile, plans, reality_checks, status

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(status.router, tags=["status"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(reality_checks.router, prefix="/reality-checks", tags=["reality-checks"])
