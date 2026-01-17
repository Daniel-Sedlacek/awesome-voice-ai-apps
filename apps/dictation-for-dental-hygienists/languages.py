"""
Language configuration for the Dental Dictation application.
Supports English, German, and Czech.
"""

# Supported languages with their Azure Speech locale codes
LANGUAGES = {
    "en-US": {
        "name": "English",
        "display": "English",
        "speech_locale": "en-US",
    },
    "de-DE": {
        "name": "German",
        "display": "Deutsch",
        "speech_locale": "de-DE",
    },
    "cs-CZ": {
        "name": "Czech",
        "display": "Čeština",
        "speech_locale": "cs-CZ",
    },
}


def get_language_options() -> list[tuple[str, str]]:
    """Get list of (locale, display_name) tuples for dropdown."""
    return [(locale, info["display"]) for locale, info in LANGUAGES.items()]


def get_speech_locale(locale: str) -> str:
    """Get the Azure Speech locale code for a given language."""
    return LANGUAGES.get(locale, LANGUAGES["en-US"])["speech_locale"]


def get_language_name(locale: str) -> str:
    """Get the display name for a given locale."""
    return LANGUAGES.get(locale, LANGUAGES["en-US"])["display"]
