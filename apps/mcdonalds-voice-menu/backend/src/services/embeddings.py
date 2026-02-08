from functools import lru_cache
from sentence_transformers import SentenceTransformer
from src.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    settings = get_settings()
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def get_detailed_instruct(task_description: str, query: str) -> str:
    """Format query with task instruction for better retrieval"""
    return f"Instruct: {task_description}\nQuery: {query}"


def create_document_embedding(text: str) -> list[float]:
    """Create embedding for a document (menu item).
    Documents don't need instruction prefix
    """
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def create_query_embedding(query: str) -> list[float]:
    """Create embedding for a query (user input).
    Queries need instruction prefix for better retrieval
    """
    model = get_embedding_model()
    task = "Given a food order query, retrieve relevant menu items that match the request."
    instruction_query = get_detailed_instruct(task, query)
    embedding = model.encode(instruction_query, normalize_embeddings=True)
    return embedding.tolist()


def create_batch_document_embeddings(texts: list[str]) -> list[list[float]]:
    """Create embeddings for multiple documents at once (more efficient)."""
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return [embedding.tolist() for embedding in embeddings]
    