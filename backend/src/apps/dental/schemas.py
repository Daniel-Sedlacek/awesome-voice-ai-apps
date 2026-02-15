"""
Request/response schemas for the dental dictation app.
"""

from typing import Annotated

import msgspec
from msgspec import Meta


class DictationRequest(msgspec.Struct):
    """Audio dictation request."""
    audio_base64: Annotated[str, Meta(min_length=1, description="Base64-encoded audio data")]
    locale: Annotated[str, Meta(description="Speech recognition locale code")] = "en-US"


class DictationResponse(msgspec.Struct):
    """Dictation response with transcription and extracted exam data."""
    transcription: Annotated[str, Meta(description="Speech-to-text transcription")]
    exam_data: Annotated[dict, Meta(description="Extracted periodontal exam data")]
    extraction_notes: Annotated[str | None, Meta(description="Notes about extraction ambiguities")] = None


class LanguageInfo(msgspec.Struct):
    """Language info for frontend."""
    locale: Annotated[str, Meta(description="Language locale code")]
    name: Annotated[str, Meta(description="Language name")]
    display: Annotated[str, Meta(description="Display label for the UI")]
    example_dictation: Annotated[str, Meta(description="Example dictation text for this language")]


class LanguagesResponse(msgspec.Struct):
    """List of available languages."""
    languages: Annotated[list[LanguageInfo], Meta(description="Available languages")]
