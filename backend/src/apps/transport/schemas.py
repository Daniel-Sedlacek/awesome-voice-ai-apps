"""
Request/response schemas for the transport translation app.
"""

from typing import Annotated

import msgspec
from msgspec import Meta


class TranslationRequest(msgspec.Struct):
    """Audio translation request."""
    audio_base64: Annotated[str, Meta(min_length=1, description="Base64-encoded audio data")]
    source_locale: Annotated[str, Meta(description="Source language locale code")]
    target_locale_1: Annotated[str, Meta(description="First target language locale code")]
    target_locale_2: Annotated[str, Meta(description="Second target language locale code")]


class LanguageResult(msgspec.Struct):
    """Translation result for a single language."""
    locale: Annotated[str, Meta(description="Language locale code")]
    text: Annotated[str, Meta(description="Translated text")]
    audio_base64: Annotated[str, Meta(description="Base64-encoded synthesized audio")]


class TranslationResponse(msgspec.Struct):
    """Full translation response with original + 2 translations."""
    original: Annotated[LanguageResult, Meta(description="Original transcription result")]
    translation_1: Annotated[LanguageResult, Meta(description="First translation result")]
    translation_2: Annotated[LanguageResult, Meta(description="Second translation result")]


class LanguageInfo(msgspec.Struct):
    """Language info for frontend."""
    locale: Annotated[str, Meta(description="Language locale code")]
    name: Annotated[str, Meta(description="Display name of the language")]


class LanguagesResponse(msgspec.Struct):
    """List of available languages."""
    languages: Annotated[list[LanguageInfo], Meta(description="Available languages")]
