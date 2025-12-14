"""Data models for the Agentic Execution Coach."""
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class EnergyLevel(str, Enum):
    """Energy/fatigue levels for weekly check-ins."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Objective(BaseModel):
    """Primary objective for the coaching period."""
    id: str = Field(..., description="Unique identifier")
    description: str = Field(..., description="Primary objective description")
    duration_weeks: int = Field(..., ge=1, description="Duration in weeks")
    created_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Version number for tracking changes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "obj_001",
                "description": "Improve strength and conditioning over 12 weeks while learning Python",
                "duration_weeks": 12,
                "version": 1
            }
        }


class HardConstraint(BaseModel):
    """Hard constraints that cannot be violated."""
    available_hours_per_week: float = Field(..., gt=0, description="Available time per week in hours")
    fixed_commitments: List[str] = Field(default_factory=list, description="Fixed commitments")
    physical_constraints: List[str] = Field(default_factory=list, description="Physical constraints")
    
    class Config:
        json_schema_extra = {
            "example": {
                "available_hours_per_week": 10.0,
                "fixed_commitments": ["Work meetings Mon/Wed 9-5", "Family time weekends"],
                "physical_constraints": ["Lower back injury - no heavy deadlifts"]
            }
        }


class NonNegotiable(BaseModel):
    """Non-negotiable rules."""
    minimum_training_frequency: int = Field(..., ge=1, description="Minimum training sessions per week")
    rest_days: List[str] = Field(..., description="Required rest days")
    other_rules: List[str] = Field(default_factory=list, description="Other immovable rules")
    
    class Config:
        json_schema_extra = {
            "example": {
                "minimum_training_frequency": 3,
                "rest_days": ["Sunday"],
                "other_rules": ["No training after 9 PM"]
            }
        }


class UserProfile(BaseModel):
    """Complete user profile with objective and constraints."""
    objective: Objective
    hard_constraints: HardConstraint
    non_negotiables: NonNegotiable
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DailyAction(BaseModel):
    """A single daily action."""
    day: str = Field(..., description="Day of week (Mon, Tue, etc.)")
    action: str = Field(..., description="Primary action for the day")
    time_estimate_minutes: int = Field(..., ge=0, description="Estimated time in minutes")
    detailed_plan: Optional[str] = Field(None, description="Detailed breakdown/training plan for this day")
    completed: bool = Field(default=False, description="Completion status")
    actual_notes: Optional[str] = Field(None, description="What was actually done on this day")
    
    @field_validator('day')
    @classmethod
    def validate_day(cls, v: str) -> str:
        valid_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        if v not in valid_days:
            raise ValueError(f"Day must be one of {valid_days}")
        return v


class WeeklyPlan(BaseModel):
    """Weekly execution plan."""
    week_id: str = Field(..., description="Week identifier (e.g., 2025-W42)")
    start_date: date = Field(..., description="Week start date")
    priorities: List[str] = Field(..., description="3-5 priorities max")
    excluded: List[str] = Field(default_factory=list, description="Explicitly excluded scope")
    daily_actions: List[DailyAction] = Field(..., description="Daily actions")
    trade_off_rationale: str = Field(..., description="Why certain goals were deprioritized")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made in planning")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "week_id": "2025-W42",
                "start_date": "2025-10-13",
                "priorities": ["Strength sessions", "Mobility work", "Learning module 3"],
                "excluded": ["Extra cardio", "New learning topics"],
                "daily_actions": [
                    {"day": "Mon", "action": "Gym session A (60 min)", "time_estimate_minutes": 60, "completed": False}
                ],
                "trade_off_rationale": "Excluded cardio to prioritize recovery and focus on strength gains",
                "assumptions": ["Energy levels will be moderate", "No unexpected work commitments"],
                "version": 1
            }
        }


class RealityCheck(BaseModel):
    """Weekly reality check input."""
    week_id: str = Field(..., description="Week identifier")
    sessions_completed: int = Field(..., ge=0, description="Sessions completed")
    sessions_planned: int = Field(..., ge=0, description="Sessions that were planned")
    energy_level: EnergyLevel = Field(..., description="Average energy/fatigue level")
    unexpected_events: List[str] = Field(default_factory=list, description="Unexpected events")
    notes: Optional[str] = Field(None, description="Additional notes")
    submitted_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "week_id": "2025-W42",
                "sessions_completed": 2,
                "sessions_planned": 4,
                "energy_level": "low",
                "unexpected_events": ["Client emergency on Tuesday", "Sick on Thursday"],
                "optional_signals": {"weight": "75kg", "subjective_stress": "high"}
            }
        }


class DeviationReport(BaseModel):
    """Deviation analysis from Reviewer agent."""
    week_id: str = Field(..., description="Week identifier")
    deviation_detected: bool = Field(..., description="Whether significant deviation occurred")
    completion_rate: float = Field(..., ge=0, le=1, description="Completion rate (0-1)")
    deviation_summary: str = Field(..., description="Summary of deviations")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in plan realism")
    recommended_action: str = Field(..., description="Recommended action (adjust/recommit)")
    created_at: datetime = Field(default_factory=datetime.now)


class AdjustmentRequest(BaseModel):
    """Request to adjust current week's plan."""
    week_id: str = Field(..., description="Week identifier")
    reason: str = Field(..., description="Reason for adjustment")
    reality_check: Optional[RealityCheck] = Field(None, description="Optional reality check data")


class ExecutionHistory(BaseModel):
    """Historical execution data for analysis."""
    week_id: str
    plan: WeeklyPlan
    reality_check: Optional[RealityCheck] = None
    deviation_report: Optional[DeviationReport] = None
    final_completion_rate: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "week_id": "2025-W42",
                "plan": {"week_id": "2025-W42"},
                "reality_check": {"week_id": "2025-W42", "sessions_completed": 3, "sessions_planned": 4},
                "deviation_report": None,
                "adjustments": [],
                "final_completion_rate": 0.75
            }
        }



