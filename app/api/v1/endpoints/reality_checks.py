"""Reality check and deviation endpoints."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.api.deps import get_orchestrator, get_state_manager
from app.models.schemas import DeviationReport, RealityCheck

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DeviationReport)
async def submit_reality_check(reality_check: RealityCheck):
    """Submit a reality check and get deviation analysis."""
    try:
        state_manager = get_state_manager()
        orchestrator = get_orchestrator()
        
        # Validate plan exists
        plan = state_manager.get_active_plan(reality_check.week_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active plan found for week {reality_check.week_id}"
            )
        
        logger.info(f"Processing reality check for {reality_check.week_id}")
        report = orchestrator.process_reality_check(reality_check)
        logger.info(f"Deviation report generated: {report.deviation_detected}")
        
        return report
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing reality check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process reality check: {str(e)}"
        )


@router.get("/deviation/{week_id}", response_model=DeviationReport)
async def get_deviation_report(week_id: str):
    """Get deviation report for a specific week."""
    state_manager = get_state_manager()
    report = state_manager.get_deviation_report(week_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No deviation report found for week {week_id}"
        )
    return report


@router.get("/history", response_model=list)
async def get_history(limit: Optional[int] = 10):
    """Get execution history."""
    state_manager = get_state_manager()
    return state_manager.get_execution_history(limit=limit)


@router.get("/history/{week_id}")
async def get_history_entry(week_id: str):
    """Get execution history for a specific week."""
    state_manager = get_state_manager()
    entry = state_manager.get_history_entry(week_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history found for week {week_id}"
        )
    return entry
