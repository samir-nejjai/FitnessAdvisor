"""Profile management endpoints."""
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_state_manager
from app.models.schemas import (
    HardConstraint,
    NonNegotiable,
    Objective,
    UserProfile,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ProfileCreateRequest(BaseModel):
    """Request model for creating user profile."""
    objective_description: str
    duration_weeks: int
    available_hours_per_week: float
    fixed_commitments: List[str]
    physical_constraints: List[str]
    minimum_training_frequency: int
    rest_days: List[str]
    other_rules: List[str]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserProfile)
async def create_profile(request: ProfileCreateRequest):
    """Create or update user profile."""
    try:
        state_manager = get_state_manager()
        
        # Check if profile exists
        existing_profile = state_manager.load_profile()
        version = 1 if not existing_profile else existing_profile.objective.version + 1
        
        # Create profile
        profile = UserProfile(
            objective=Objective(
                id=f"obj_{version:03d}",
                description=request.objective_description,
                duration_weeks=request.duration_weeks,
                version=version
            ),
            hard_constraints=HardConstraint(
                available_hours_per_week=request.available_hours_per_week,
                fixed_commitments=request.fixed_commitments,
                physical_constraints=request.physical_constraints
            ),
            non_negotiables=NonNegotiable(
                minimum_training_frequency=request.minimum_training_frequency,
                rest_days=request.rest_days,
                other_rules=request.other_rules
            )
        )
        
        state_manager.save_profile(profile)
        logger.info(f"Profile created/updated: version {version}")
        
        return profile
    
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("", response_model=UserProfile)
async def get_profile():
    """Get current user profile."""
    state_manager = get_state_manager()
    profile = state_manager.load_profile()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create a profile first."
        )
    return profile
