import logging
from functools import lru_cache

from sentence_transformers import CrossEncoder

from src.settings import get_settings
from src.models import MenuItem

logger = logging.getLogger(__name__)

RERANKER_SCORE_THRESHOLD = -8.0


@lru_cache(maxsize=1)
def get_reranker_model() -> CrossEncoder:
    """Load and cache the cross-encoder reranker model."""
    settings = get_settings()
    return CrossEncoder(settings.RERANKER_MODEL_NAME)


def rerank_items(query: str, items: list[MenuItem]) -> list[MenuItem]:
    """Rerank menu items using a cross-encoder, filtering by score threshold."""
    if not items:
        return []

    model = get_reranker_model()

    pairs = []
    for item in items:
        tags_str = ", ".join(item.tags) if item.tags else ""
        doc_text = f"{item.name}: {item.description} ({tags_str})"
        pairs.append((query, doc_text))

    scores = model.predict(pairs)

    scored_items = list(zip(items, scores))
    scored_items.sort(key=lambda x: x[1], reverse=True)

    for item, score in scored_items:
        logger.info("Rerank: '%s' score=%.4f", item.name, float(score))

    filtered = [
        item for item, score in scored_items
        if float(score) >= RERANKER_SCORE_THRESHOLD
    ]

    logger.info("Reranker kept %d/%d items (threshold=%.2f)", len(filtered), len(items), RERANKER_SCORE_THRESHOLD)
    return filtered
