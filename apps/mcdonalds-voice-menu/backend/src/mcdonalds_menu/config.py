from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Azure Speech
    AZURE_SPEECH_KEY: str
    AZURE_SPEECH_REGION: str

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str

    #Database
    DATABASE_URL: str = "postgresql+asyncpg://mcdonalds:mcdonalds@localhost:5432/mcdonalds_menu"

    # Embeddin model
    EMBEDDING_MODEL_NAME: str = "intfload/multilingual-e5-large-instruct"
    EMBEDDING_DIMENSION: int = 1024



@lru_cache
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()