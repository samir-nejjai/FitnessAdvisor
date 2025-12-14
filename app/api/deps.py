"""API dependencies."""
from app.services.state_manager import StateManager
from app.services.workflows import WorkflowOrchestrator


def get_state_manager() -> StateManager:
    """Get StateManager instance."""
    return StateManager()


def get_orchestrator() -> WorkflowOrchestrator:
    """Get WorkflowOrchestrator instance."""
    return WorkflowOrchestrator()
