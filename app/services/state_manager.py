"""Simplified state management with single JSON file."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.models.schemas import (
    DeviationReport,
    ExecutionHistory,
    RealityCheck,
    UserProfile,
    WeeklyPlan,
)
from app.core.config import settings


class StateManager:
    """Manages application state with single JSON file."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize state manager.
        
        Args:
            data_dir: Directory for storing data files. Defaults to settings.data_dir
        """
        self.data_dir = data_dir or settings.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "state.json"
    
    def _load_state(self) -> Dict:
        """Load entire state from file."""
        if not self.state_file.exists():
            return {"profile": None, "plans": [], "history": []}
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _save_state(self, state: Dict) -> None:
        """Save entire state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    # User Profile Management
    
    def save_profile(self, profile: UserProfile) -> None:
        """Save user profile."""
        profile.updated_at = datetime.now()
        state = self._load_state()
        state["profile"] = profile.model_dump(mode='json')
        self._save_state(state)
    
    def load_profile(self) -> Optional[UserProfile]:
        """Load user profile."""
        state = self._load_state()
        if not state.get("profile"):
            return None
        return UserProfile.model_validate(state["profile"])
    
    def profile_exists(self) -> bool:
        """Check if profile exists."""
        state = self._load_state()
        return state.get("profile") is not None
    
    # Weekly Plans Management
    
    def save_plan(self, plan: WeeklyPlan) -> None:
        """Save a weekly plan."""
        state = self._load_state()
        plans = state.get("plans", [])
        
        # Replace existing plan for same week (no versioning)
        plans = [p for p in plans if p["week_id"] != plan.week_id]
        plans.append(plan.model_dump(mode='json'))
        
        state["plans"] = plans
        self._save_state(state)
    
    def get_active_plan(self, week_id: str) -> Optional[WeeklyPlan]:
        """Get plan for a specific week."""
        state = self._load_state()
        plans = state.get("plans", [])
        
        for plan_data in plans:
            if plan_data["week_id"] == week_id:
                return WeeklyPlan.model_validate(plan_data)
        return None
    
    def get_all_plans(self) -> List[WeeklyPlan]:
        """Get all plans."""
        state = self._load_state()
        return [WeeklyPlan.model_validate(p) for p in state.get("plans", [])]
    

    
    # Execution History Management
    
    def save_history_entry(self, entry: ExecutionHistory) -> None:
        """Save an execution history entry."""
        state = self._load_state()
        history = state.get("history", [])
        
        # Update or append
        history = [h for h in history if h["week_id"] != entry.week_id]
        history.append(entry.model_dump(mode='json'))
        
        state["history"] = history
        self._save_state(state)
    
    def save_reality_check(self, reality_check: RealityCheck) -> None:
        """Save reality check to history."""
        history = self.get_history_entry(reality_check.week_id)
        if history:
            history.reality_check = reality_check
            self.save_history_entry(history)
    
    def save_deviation_report(self, report: DeviationReport) -> None:
        """Save deviation report to history."""
        history = self.get_history_entry(report.week_id)
        if history:
            history.deviation_report = report
            history.final_completion_rate = report.completion_rate
            self.save_history_entry(history)
    
    def get_history_entry(self, week_id: str) -> Optional[ExecutionHistory]:
        """Get execution history for a specific week."""
        state = self._load_state()
        history = state.get("history", [])
        
        for entry_data in history:
            if entry_data["week_id"] == week_id:
                return ExecutionHistory.model_validate(entry_data)
        return None
    
    def get_deviation_report(self, week_id: str) -> Optional[DeviationReport]:
        """Get deviation report from history."""
        history = self.get_history_entry(week_id)
        return history.deviation_report if history else None
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[ExecutionHistory]:
        """Get execution history, optionally limited to recent entries."""
        state = self._load_state()
        history_data = state.get("history", [])
        
        # Sort by week_id descending
        history_data.sort(key=lambda x: x["week_id"], reverse=True)
        
        if limit:
            history_data = history_data[:limit]
        
        return [ExecutionHistory.model_validate(h) for h in history_data]
    
    # Utility Methods
    
    def clear_all_data(self) -> None:
        """Clear all data. Use with caution!"""
        if self.state_file.exists():
            self.state_file.unlink()
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored data."""
        state = self._load_state()
        return {
            "profile_exists": self.profile_exists(),
            "total_plans": len(state.get("plans", [])),
            "total_history_entries": len(state.get("history", [])),
        }
