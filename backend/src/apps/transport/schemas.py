"""
Request/response schemas for the transport translation app.
"""

import msgspec


class TranslationRequest(msgspec.Struct):
    """Audio translation request."""
    audio_base64: str
    source_locale: str
    target_locale_1: str
    target_locale_2: str


class LanguageResult(msgspec.Struct):
    """Translation result for a single language."""
    locale: str
    text: str
    audio_base64: str


class TranslationResponse(msgspec.Struct):
    """Full translation response with original + 2 translations."""
    original: LanguageResult
    translation_1: LanguageResult
    translation_2: LanguageResult


class LanguageInfo(msgspec.Struct):
    """Language info for frontend."""
    locale: str
    name: str


class LanguagesResponse(msgspec.Struct):
    """List of available languages."""
    languages: list[LanguageInfo]
