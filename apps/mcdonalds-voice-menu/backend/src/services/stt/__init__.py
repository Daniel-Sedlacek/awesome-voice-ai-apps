from collections.abc import Callable

from src.settings import get_settings
from src.services.stt.streaming import StreamingSTTSession


async def transcribe_audio(
    audio_data: bytes,
    language: str = "en-US",
    on_interim: Callable[[str], None] | None = None,
) -> str:
    """Transcribe audio using the configured STT provider."""
    settings = get_settings()
    if settings.STT_PROVIDER == "deepgram":
        from src.services.stt.deepgram_provider import transcribe_audio as _transcribe
    else:
        from src.services.stt.azure_provider import transcribe_audio as _transcribe
    return await _transcribe(audio_data, language, on_interim)


def create_streaming_session() -> StreamingSTTSession:
    """Create a streaming STT session using the configured provider."""
    settings = get_settings()
    if settings.STT_PROVIDER == "deepgram":
        from src.services.stt.deepgram_provider import DeepgramStreamingSession
        return DeepgramStreamingSession()
    else:
        from src.services.stt.azure_provider import AzureStreamingSession
        return AzureStreamingSession()
