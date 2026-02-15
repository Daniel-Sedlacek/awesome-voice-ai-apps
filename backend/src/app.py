import logging

from huggingface_hub import try_to_load_from_cache
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.static_files import StaticFilesConfig

from src.apps.mcdonalds.routes.audio import AudioController
from src.apps.mcdonalds.routes.audio_ws import AudioWSListener
from src.apps.mcdonalds.routes.menu import MenuController
from src.apps.mcdonalds.services.embeddings import get_embedding_model
from src.apps.mcdonalds.services.reranker import get_reranker_model
from src.apps.transport.routes.translate import TranslateController
from src.apps.dental.routes.dictation import DictationController
from src.apps.psychotherapy.routes.analysis import AnalysisController
from src.settings import get_settings

logger = logging.getLogger(__name__)


def _is_model_cached(repo_id: str) -> bool:
    """Check if a Hugging Face model is already downloaded locally."""
    result = try_to_load_from_cache(repo_id, "config.json")
    return isinstance(result, str)


async def preload_models() -> None:
    """Download embedding and reranker models at startup if not already cached."""
    settings = get_settings()

    if _is_model_cached(settings.EMBEDDING_MODEL_NAME):
        logger.info("Embedding model already cached, skipping download.")
    else:
        logger.info("Downloading embedding model...")
        get_embedding_model()
        logger.info("Embedding model downloaded.")

    if _is_model_cached(settings.RERANKER_MODEL_NAME):
        logger.info("Reranker model already cached, skipping download.")
    else:
        logger.info("Downloading reranker model...")
        get_reranker_model()
        logger.info("Reranker model downloaded.")


# CORS configuration for frontend
cors_config = CORSConfig(
    allow_origins=["http://localhost:5173", "ws://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app = Litestar(
    route_handlers=[
        # McDonald's
        AudioController,
        MenuController,
        AudioWSListener,
        # Transport
        TranslateController,
        # Dental
        DictationController,
        # Psychotherapy
        AnalysisController,
    ],
    cors_config=cors_config,
    static_files_config=[
        StaticFilesConfig(
            directories=["static"],
            path="/static",
        )
    ],
    on_startup=[preload_models],
    debug=True,
)
