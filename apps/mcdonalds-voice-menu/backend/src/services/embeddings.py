from functools import lru_cache
from sentence_transformers import SentenceTransformer
from src.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    settings = get_settings()
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def create_document_embedding(text: str) -> list[float]:
    """Create embedding for a document (menu item)."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def create_query_embedding(query: str) -> list[float]:
    """Create embedding for a query (user input)."""
    model = get_embedding_model()
    embedding = model.encode(query, normalize_embeddings=True)
    return embedding.tolist()


def create_batch_document_embeddings(texts: list[str]) -> list[list[float]]:
    """Create embeddings for multiple documents at once (more efficient)."""
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return [embedding.tolist() for embedding in embeddings]
