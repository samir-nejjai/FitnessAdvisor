"""
Utility script to test LLM configuration without running the full app.
"""
from llm_factory import LLMFactory
from config import settings

def test_llm_configuration():
    """Test LLM configuration and connectivity."""
    print("🔍 Testing LLM Configuration\n")
    print(f"Current provider: {settings.llm_provider}\n")
    
    # Validate configuration
    print("Validating credentials...")
    validation = LLMFactory.validate_configuration()
    
    for provider, is_valid in validation.items():
        status = "✅" if is_valid else "❌"
        print(f"  {status} {provider}: {'Configured' if is_valid else 'Not configured'}")
    
    print()
    
    # Get available providers
    available = LLMFactory.get_available_providers()
    print(f"Available providers: {', '.join(available) if available else 'None'}")
    print()
    
    # Try to create LLM instance
    if settings.llm_provider in available:
        try:
            print(f"Creating {settings.llm_provider} instance...")
            llm = LLMFactory.create_llm()
            print(f"✅ Successfully created LLM instance")
            print(f"   Type: {type(llm).__name__}")
            
            # Test with a simple prompt
            print("\nTesting with simple prompt...")
            response = llm.invoke("Say 'Hello from the Execution Coach!' in one sentence.")
            print(f"✅ Response: {response.content}")
            
        except Exception as e:
            print(f"❌ Error creating/testing LLM: {e}")
    else:
        print(f"⚠️  Provider '{settings.llm_provider}' is not properly configured")
        print("   Please check your .env file")

if __name__ == "__main__":
    test_llm_configuration()
