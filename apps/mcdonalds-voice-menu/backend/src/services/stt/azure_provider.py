import asyncio
from collections.abc import Callable, Awaitable

import azure.cognitiveservices.speech as speechsdk

from src.settings import get_settings
from src.services.stt.phrase_hints import get_menu_phrases
from src.services.stt.streaming import StreamingSTTSession


class AzureStreamingSession(StreamingSTTSession):
    """Streaming STT using Azure continuous recognition."""

    def __init__(self) -> None:
        self._stream: speechsdk.audio.PushAudioInputStream | None = None
        self._recognizer: speechsdk.SpeechRecognizer | None = None
        self._on_interim: Callable[[str], Awaitable[None]] | None = None
        self._on_final: Callable[[str], Awaitable[None]] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def start(
        self,
        language: str,
        on_interim: Callable[[str], Awaitable[None]],
        on_final: Callable[[str], Awaitable[None]],
    ) -> None:
        settings = get_settings()
        self._on_interim = on_interim
        self._on_final = on_final
        self._loop = asyncio.get_running_loop()

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION,
        )
        speech_config.speech_recognition_language = language

        self._stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=self._stream)

        self._recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        phrases = get_menu_phrases(language)
        phrase_list = speechsdk.PhraseListGrammar.from_recognizer(self._recognizer)
        for phrase in phrases:
            phrase_list.addPhrase(phrase)

        self._recognizer.recognizing.connect(self._handle_recognizing)
        self._recognizer.recognized.connect(self._handle_recognized)

        self._recognizer.start_continuous_recognition()

    def _handle_recognizing(self, evt: speechsdk.SpeechRecognitionEventArgs) -> None:
        if self._on_interim and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._on_interim(evt.result.text), self._loop
            )

    def _handle_recognized(self, evt: speechsdk.SpeechRecognitionEventArgs) -> None:
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech and self._on_final and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._on_final(evt.result.text), self._loop
            )

    async def send_audio(self, chunk: bytes) -> None:
        if self._stream:
            self._stream.write(chunk)

    async def stop(self) -> None:
        if self._stream:
            self._stream.close()
        if self._recognizer:
            self._recognizer.stop_continuous_recognition()
            self._recognizer = None
        self._stream = None
