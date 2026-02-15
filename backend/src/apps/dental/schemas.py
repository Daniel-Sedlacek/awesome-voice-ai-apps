"""
Request/response schemas for the dental dictation app.
"""

import msgspec


class DictationRequest(msgspec.Struct):
    """Audio dictation request."""
    audio_base64: str
    locale: str = "en-US"


class DictationResponse(msgspec.Struct):
    """Dictation response with transcription and extracted exam data."""
    transcription: str
    exam_data: dict
    extraction_notes: str | None = None


class LanguageInfo(msgspec.Struct):
    """Language info for frontend."""
    locale: str
    name: str
    display: str
    example_dictation: str


class LanguagesResponse(msgspec.Struct):
    """List of available languages."""
    languages: list[LanguageInfo]
