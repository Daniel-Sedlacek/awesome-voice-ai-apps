import logging

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

logger = logging.getLogger(__name__)


async def preload_models() -> None:
    """Pre-download and load the embedding and reranker models at server startup."""
    logger.info("Loading embedding model...")
    get_embedding_model()
    logger.info("Embedding model loaded.")
    logger.info("Loading reranker model...")
    get_reranker_model()
    logger.info("Reranker model loaded.")


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
