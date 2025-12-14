"""Weekly plan endpoints."""
import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_orchestrator, get_state_manager
from app.models.schemas import AdjustmentRequest, WeeklyPlan

router = APIRouter()
logger = logging.getLogger(__name__)


class WeeklyPlanRequest(BaseModel):
    """Request model for generating weekly plan."""
    week_start_date: Optional[str] = None  # ISO format YYYY-MM-DD


@router.post("/generate", status_code=status.HTTP_201_CREATED, response_model=WeeklyPlan)
async def generate_weekly_plan(request: WeeklyPlanRequest):
    """Generate a new weekly plan."""
    try:
        state_manager = get_state_manager()
        orchestrator = get_orchestrator()
        
        # Validate profile exists
        if not state_manager.profile_exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile must be created before generating plans"
            )
        
        # Parse date if provided
        week_start = None
        if request.week_start_date:
            try:
                week_start = date.fromisoformat(request.week_start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        # Generate plan
        logger.info(f"Generating weekly plan for {week_start or 'next week'}")
        plan = orchestrator.generate_weekly_plan(week_start_date=week_start)
        logger.info(f"Plan generated: {plan.week_id}")
        
        return plan
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}"
        )


@router.get("", response_model=List[WeeklyPlan])
async def get_all_plans():
    """Get all plans."""
    state_manager = get_state_manager()
    return state_manager.get_all_plans()


@router.get("/latest", response_model=WeeklyPlan)
async def get_latest_plan():
    """Get the most recent plan."""
    state_manager = get_state_manager()
    plans = state_manager.get_all_plans()
    if not plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plans found"
        )
    # Plans are sorted by week_id, get the last one
    return sorted(plans, key=lambda p: p.week_id, reverse=True)[0]


@router.get("/{week_id}", response_model=WeeklyPlan)
async def get_plan(week_id: str):
    """Get active plan for a specific week."""
    state_manager = get_state_manager()
    plan = state_manager.get_active_plan(week_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active plan found for week {week_id}"
        )
    return plan


@router.post("/adjust", status_code=status.HTTP_201_CREATED, response_model=WeeklyPlan)
async def adjust_plan(adjustment: AdjustmentRequest):
    """Adjust the current week's plan."""
    try:
        orchestrator = get_orchestrator()
        logger.info(f"Adjusting plan for {adjustment.week_id}")
        adjusted_plan = orchestrator.adjust_plan(adjustment)
        logger.info(f"Plan adjusted for {adjusted_plan.week_id}")
        
        return adjusted_plan
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adjusting plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adjust plan: {str(e)}"
        )
