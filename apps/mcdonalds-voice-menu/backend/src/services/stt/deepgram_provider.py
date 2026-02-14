import asyncio
from collections.abc import Callable

from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

from src.settings import get_settings
from src.services.stt.phrase_hints import get_menu_phrases

_LOCALE_TO_LANG = {
    "en-US": "en",
    "de-DE": "de",
    "cs-CZ": "cs",
}


async def transcribe_audio(
    audio_data: bytes,
    language: str = "en-US",
    on_interim: Callable[[str], None] | None = None,
) -> str:
    """Transcribe audio using Deepgram's live streaming API."""
    settings = get_settings()
    client = DeepgramClient(settings.DEEPGRAM_API_KEY)
    lang_code = _LOCALE_TO_LANG.get(language, language)
    phrases = get_menu_phrases(language)
    keywords = [f"{p}:2" for p in phrases]

    done = asyncio.Event()
    final_parts: list[str] = []

    options = LiveOptions(
        model="nova-3",
        language=lang_code,
        smart_format=True,
        interim_results=on_interim is not None,
        utterance_end_ms="1000",
        keywords=keywords,
    )

    connection = client.listen.live.v("1")

    def on_message(self, result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        if not transcript:
            return
        if result.is_final:
            final_parts.append(transcript)
        elif on_interim:
            on_interim(transcript)

    def on_close(self, *args, **kwargs):
        done.set()

    def on_error(self, error, **kwargs):
        done.set()

    connection.on(LiveTranscriptionEvents.Transcript, on_message)
    connection.on(LiveTranscriptionEvents.Close, on_close)
    connection.on(LiveTranscriptionEvents.Error, on_error)

    connection.start(options)
    connection.send(audio_data)
    connection.finish()
    await done.wait()

    return " ".join(final_parts).strip()
