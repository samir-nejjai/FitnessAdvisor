"""Status and system information endpoints."""
import logging
from datetime import date
from typing import Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import get_state_manager
from app.models.schemas import WeeklyPlan

router = APIRouter()
logger = logging.getLogger(__name__)


class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    profile_exists: bool
    current_week_id: Optional[str]
    active_plan: Optional[WeeklyPlan]
    statistics: Dict


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current system status."""
    state_manager = get_state_manager()
    
    profile_exists = state_manager.profile_exists()
    
    # Calculate current week_id
    today = date.today()
    current_week_id = f"{today.year}-W{today.isocalendar()[1]:02d}"
    
    # Get active plan if exists
    active_plan = state_manager.get_active_plan(current_week_id)
    
    # Get statistics
    stats = state_manager.get_statistics()
    
    return StatusResponse(
        profile_exists=profile_exists,
        current_week_id=current_week_id,
        active_plan=active_plan,
        statistics=stats
    )
