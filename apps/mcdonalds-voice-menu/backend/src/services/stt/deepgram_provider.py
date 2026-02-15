import asyncio
from collections.abc import Callable, Awaitable

from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1ControlMessage

from src.settings import get_settings
from src.services.stt.phrase_hints import get_menu_phrases
from src.services.stt.streaming import StreamingSTTSession

_LOCALE_TO_LANG = {
    "en-US": "en",
    "de-DE": "de",
    "cs-CZ": "cs",
}


class DeepgramStreamingSession(StreamingSTTSession):
    """Streaming STT using Deepgram's async WebSocket API.

    The Deepgram WebSocket connection is opened lazily on the first
    ``send_audio`` call so that Deepgram's inactivity timer doesn't
    expire while the browser is still setting up the microphone.
    """

    def __init__(self) -> None:
        self._connection = None
        self._ctx_manager = None
        self._listener_task: asyncio.Task | None = None
        self._on_interim: Callable[[str], Awaitable[None]] | None = None
        self._on_final: Callable[[str], Awaitable[None]] | None = None
        self._language: str = "en"
        self._keyterms: list[str] = []
        self._started = False

    async def start(
        self,
        language: str,
        on_interim: Callable[[str], Awaitable[None]],
        on_final: Callable[[str], Awaitable[None]],
    ) -> None:
        self._on_interim = on_interim
        self._on_final = on_final
        self._language = _LOCALE_TO_LANG.get(language, language)
        phrases = get_menu_phrases(language)
        self._keyterms = [f"{p}:2" for p in phrases]

    async def _ensure_connected(self) -> None:
        """Open the Deepgram WebSocket on first use (async)."""
        if self._started:
            return
        self._started = True
        settings = get_settings()
        client = AsyncDeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
        self._ctx_manager = client.listen.v1.connect(
            model="nova-3",
            language=self._language,
            smart_format="true",
            interim_results="true",
            utterance_end_ms="1000",
            encoding="linear16",
            sample_rate=16000,
            channels=1,
            keyterm=self._keyterms,
        )
        self._connection = await self._ctx_manager.__aenter__()
        self._connection.on(EventType.MESSAGE, self._handle_message)
        # start_listening is a long-running coroutine; run it in background
        self._listener_task = asyncio.create_task(self._connection.start_listening())

    async def _handle_message(self, result) -> None:
        if getattr(result, "type", None) != "Results":
            return
        transcript = result.channel.alternatives[0].transcript
        if not transcript:
            return
        if result.is_final:
            if self._on_final:
                await self._on_final(transcript)
        elif self._on_interim:
            await self._on_interim(transcript)

    async def send_audio(self, chunk: bytes) -> None:
        await self._ensure_connected()
        if self._connection:
            await self._connection.send_media(chunk)

    async def stop(self) -> None:
        if self._connection:
            try:
                await self._connection.send_control(ListenV1ControlMessage(type="Finalize"))
            except Exception:
                pass
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except (asyncio.CancelledError, Exception):
                pass
            self._listener_task = None
        if self._ctx_manager:
            try:
                await self._ctx_manager.__aexit__(None, None, None)
            except Exception:
                pass
            self._ctx_manager = None
        self._connection = None
