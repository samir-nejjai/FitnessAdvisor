"""
Basic tests for the Agentic Execution Coach.
Run with: pytest test_basic.py
"""
import pytest
from datetime import date
from models import (
    Objective,
    HardConstraint,
    NonNegotiable,
    UserProfile,
    WeeklyPlan,
    DailyAction,
    RealityCheck,
    EnergyLevel,
)
from state_manager import StateManager
from config import settings
import tempfile
from pathlib import Path


@pytest.fixture
def temp_state_manager():
    """Create a state manager with temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield StateManager(data_dir=Path(tmpdir))


@pytest.fixture
def sample_profile():
    """Create a sample user profile."""
    return UserProfile(
        objective=Objective(
            id="test_obj_001",
            description="Test objective",
            duration_weeks=12,
            version=1
        ),
        hard_constraints=HardConstraint(
            available_hours_per_week=10.0,
            fixed_commitments=["Work Mon-Fri"],
            physical_constraints=[]
        ),
        non_negotiables=NonNegotiable(
            minimum_training_frequency=3,
            rest_days=["Sunday"],
            other_rules=[]
        )
    )


@pytest.fixture
def sample_plan():
    """Create a sample weekly plan."""
    return WeeklyPlan(
        week_id="2025-W50",
        start_date=date(2025, 12, 15),
        priorities=["Priority 1", "Priority 2", "Priority 3"],
        excluded=["Excluded item"],
        daily_actions=[
            DailyAction(day="Mon", action="Action 1", time_estimate_minutes=60),
            DailyAction(day="Tue", action="Action 2", time_estimate_minutes=45),
        ],
        trade_off_rationale="Test rationale",
        assumptions=["Assumption 1"]
    )


class TestModels:
    """Test Pydantic models."""
    
    def test_objective_creation(self):
        """Test creating an objective."""
        obj = Objective(
            id="test_001",
            description="Test objective",
            duration_weeks=12,
            version=1
        )
        assert obj.id == "test_001"
        assert obj.duration_weeks == 12
    
    def test_weekly_plan_priorities_validation(self):
        """Test that priorities must be 3-5 items."""
        with pytest.raises(ValueError):
            WeeklyPlan(
                week_id="2025-W50",
                start_date=date(2025, 12, 15),
                priorities=["Only one"],  # Too few
                excluded=[],
                daily_actions=[],
                trade_off_rationale="Test"
            )
    
    def test_daily_action_day_validation(self):
        """Test that day must be valid."""
        with pytest.raises(ValueError):
            DailyAction(
                day="Monday",  # Should be "Mon"
                action="Test",
                time_estimate_minutes=60
            )
    
    def test_reality_check_creation(self):
        """Test creating a reality check."""
        rc = RealityCheck(
            week_id="2025-W50",
            sessions_completed=3,
            sessions_planned=4,
            energy_level=EnergyLevel.MODERATE
        )
        assert rc.week_id == "2025-W50"
        assert rc.energy_level == EnergyLevel.MODERATE


class TestStateManager:
    """Test state management."""
    
    def test_save_and_load_profile(self, temp_state_manager, sample_profile):
        """Test saving and loading profile."""
        temp_state_manager.save_profile(sample_profile)
        loaded = temp_state_manager.load_profile()
        
        assert loaded is not None
        assert loaded.objective.description == sample_profile.objective.description
    
    def test_profile_exists(self, temp_state_manager, sample_profile):
        """Test profile existence check."""
        assert not temp_state_manager.profile_exists()
        
        temp_state_manager.save_profile(sample_profile)
        assert temp_state_manager.profile_exists()
    
    def test_save_and_get_plan(self, temp_state_manager, sample_plan):
        """Test saving and retrieving plan."""
        temp_state_manager.save_plan(sample_plan)
        loaded = temp_state_manager.get_active_plan(sample_plan.week_id)
        
        assert loaded is not None
        assert loaded.week_id == sample_plan.week_id
        assert len(loaded.priorities) == len(sample_plan.priorities)
    
    def test_plan_versioning(self, temp_state_manager, sample_plan):
        """Test that newer plan versions deactivate older ones."""
        temp_state_manager.save_plan(sample_plan)
        
        # Create adjusted version
        adjusted = sample_plan.model_copy()
        adjusted.version = 2
        adjusted.priorities = ["Adjusted priority"]
        
        temp_state_manager.save_plan(adjusted)
        
        # Only adjusted plan should be active
        active = temp_state_manager.get_active_plan(sample_plan.week_id)
        assert active.version == 2
        
        # But we should have both versions in history
        all_plans = temp_state_manager.get_plans_by_week(sample_plan.week_id)
        assert len(all_plans) == 2
    
    def test_get_statistics(self, temp_state_manager, sample_profile, sample_plan):
        """Test getting statistics."""
        stats = temp_state_manager.get_statistics()
        assert stats["profile_exists"] is False
        assert stats["total_plans"] == 0
        
        temp_state_manager.save_profile(sample_profile)
        temp_state_manager.save_plan(sample_plan)
        
        stats = temp_state_manager.get_statistics()
        assert stats["profile_exists"] is True
        assert stats["total_plans"] == 1


class TestConfig:
    """Test configuration."""
    
    def test_settings_loaded(self):
        """Test that settings are loaded."""
        assert settings.llm_provider in ["azure_openai", "openai", "gemini"]
        assert settings.data_dir is not None
    
    def test_data_dir_creation(self):
        """Test that data directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import Settings
            test_settings = Settings(data_dir=Path(tmpdir) / "test_data")
            assert test_settings.data_dir.exists()


class TestLLMFactory:
    """Test LLM factory (configuration only, not actual LLM calls)."""
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        from llm_factory import LLMFactory
        
        validation = LLMFactory.validate_configuration()
        assert isinstance(validation, dict)
        assert "azure_openai" in validation
        assert "openai" in validation
        assert "gemini" in validation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
