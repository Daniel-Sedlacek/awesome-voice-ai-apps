from msgspec_ext import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
    )

    # Azure Speech (all apps use STT)
    AZURE_SPEECH_KEY: str
    AZURE_SPEECH_REGION: str = "westeurope"

    # Azure OpenAI (mcdonalds, dental, psychotherapy)
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4.1-mini"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"

    # Azure Translator (transport only)
    AZURE_TRANSLATOR_KEY: str = ""
    AZURE_TRANSLATOR_REGION: str = "westeurope"

    # Database (mcdonalds only)
    DATABASE_URL: str = "postgresql+asyncpg://mcdonalds:mcdonalds@localhost:5432/mcdonalds_menu"

    # Embedding model (mcdonalds only)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384

    # Reranker model (mcdonalds only)
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # STT provider
    STT_PROVIDER: str = "azure"  # "azure" or "deepgram"
    DEEPGRAM_API_KEY: str = ""


def get_settings() -> Settings:
    """Get settings instance (cached internally by msgspec-ext after first load)."""
    return Settings()
