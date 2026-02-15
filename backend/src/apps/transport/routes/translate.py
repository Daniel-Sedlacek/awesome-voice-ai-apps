"""
Transport translation API routes.
"""

import base64

from litestar import Controller, get, post

from src.apps.transport.schemas import (
    LanguageInfo,
    LanguageResult,
    LanguagesResponse,
    TranslationRequest,
    TranslationResponse,
)
from src.apps.transport.services.translation import process_recording
from src.apps.transport.languages import LANGUAGES


class TranslateController(Controller):
    path = "/api/transport"

    @post("/process")
    async def process_audio(self, data: TranslationRequest) -> TranslationResponse:
        """Process audio: transcribe, translate to 2 languages, synthesize TTS."""
        audio_data = base64.b64decode(data.audio_base64)
        result = process_recording(
            audio_data, data.source_locale, data.target_locale_1, data.target_locale_2
        )
        return TranslationResponse(
            original=LanguageResult(**result["original"]),
            translation_1=LanguageResult(**result["translation_1"]),
            translation_2=LanguageResult(**result["translation_2"]),
        )

    @get("/languages")
    async def get_languages(self) -> LanguagesResponse:
        """Get available languages."""
        return LanguagesResponse(
            languages=[
                LanguageInfo(locale=locale, name=info["name"])
                for locale, info in LANGUAGES.items()
            ]
        )
