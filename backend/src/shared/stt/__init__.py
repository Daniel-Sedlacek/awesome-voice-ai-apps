from src.settings import get_settings
from src.shared.stt.streaming import StreamingSTTSession
import logging

logger = logging.getLogger(__name__)


def create_streaming_session() -> StreamingSTTSession:
    """Create a streaming STT session using the configured provider."""
    settings = get_settings()
    logger.info(f"Creating streaming session using {settings.STT_PROVIDER} as a STT provider")
    if settings.STT_PROVIDER == "deepgram":
        from src.shared.stt.deepgram_provider import DeepgramStreamingSession
        return DeepgramStreamingSession()
    elif settings.STT_PROVIDER == "azure":
        from src.shared.stt.azure_provider import AzureStreamingSession
        return AzureStreamingSession()
    else:
        raise ValueError(f"Invalid STT provider: {settings.STT_PROVIDER}")
