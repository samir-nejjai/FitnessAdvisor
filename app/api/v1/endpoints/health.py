"""Health check endpoints."""
from fastapi import APIRouter

from app.core.config import settings
from app.services.llm_factory import LLMFactory

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    llm_config = LLMFactory.validate_configuration()
    available_providers = LLMFactory.get_available_providers()
    
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "llm_configured": llm_config,
        "available_providers": available_providers,
        "data_directory": str(settings.data_dir),
    }
