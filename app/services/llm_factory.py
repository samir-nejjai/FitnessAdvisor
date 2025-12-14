"""Simplified LLM factory - Azure OpenAI only."""
from langchain_openai import AzureChatOpenAI
from app.core.config import settings


class LLMFactory:
    """Factory for creating LLM instances."""
    
    @staticmethod
    def create_llm(temperature: float = 0.7, **kwargs):
        """Create an Azure OpenAI LLM instance.
        
        Args:
            temperature: Temperature for generation (0-1)
            **kwargs: Additional arguments
            
        Returns:
            LLM instance
            
        Raises:
            ValueError: If Azure OpenAI credentials are missing
        """
        if not settings.azure_openai_api_key:
            raise ValueError(
                "Azure OpenAI API key not configured. "
                "Set AZURE_OPENAI_API_KEY in environment variables."
            )
        
        if not settings.azure_openai_endpoint:
            raise ValueError(
                "Azure OpenAI endpoint not configured. "
                "Set AZURE_OPENAI_ENDPOINT in environment variables."
            )
        
        return AzureChatOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.azure_openai_deployment_name,
            api_version=settings.azure_openai_api_version,
            temperature=temperature,
            **kwargs
        )
