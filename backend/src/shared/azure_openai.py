"""
Unified Azure OpenAI client factory.
"""

from openai import OpenAI

from src.settings import get_settings


def get_openai_client() -> OpenAI:
    """Get OpenAI client configured for Azure AI Foundry."""
    settings = get_settings()
    return OpenAI(
        api_key=settings.AZURE_OPENAI_KEY,
        base_url=settings.AZURE_OPENAI_ENDPOINT,
    )
