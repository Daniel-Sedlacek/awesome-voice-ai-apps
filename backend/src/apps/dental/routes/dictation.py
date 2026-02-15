"""
Dental dictation API routes.
"""

import base64

from litestar import Controller, get, post

from src.shared.azure_stt import transcribe_audio_continuous
from src.apps.dental.schemas import (
    DictationRequest,
    DictationResponse,
    LanguageInfo,
    LanguagesResponse,
)
from src.apps.dental.services.extraction import extract_periodontal_data
from src.apps.dental.languages import LANGUAGES


class DictationController(Controller):
    path = "/api/dental"

    @post("/process")
    async def process_dictation(self, data: DictationRequest) -> DictationResponse:
        """Process audio dictation: transcribe and extract periodontal data."""
        audio_data = base64.b64decode(data.audio_base64)

        # Continuous recognition for longer dictations
        transcription = transcribe_audio_continuous(audio_data, data.locale)

        # Extract structured periodontal data
        exam = extract_periodontal_data(transcription)

        return DictationResponse(
            transcription=transcription,
            exam_data=exam.model_dump(),
            extraction_notes=exam.extraction_notes,
        )

    @get("/languages")
    async def get_languages(self) -> LanguagesResponse:
        """Get available languages with example dictations."""
        return LanguagesResponse(
            languages=[
                LanguageInfo(
                    locale=locale,
                    name=info["name"],
                    display=info["display"],
                    example_dictation=info["example_dictation"],
                )
                for locale, info in LANGUAGES.items()
            ]
        )
