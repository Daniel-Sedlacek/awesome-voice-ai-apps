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
        "example_dictation": (
            "Tooth 14, pocket depth 4 millimeters on the mesial, bleeding on probing. "
            "Tooth 26, recession 2 millimeters on the buccal side. "
            "Tooth 36, pocket depth 5 millimeters distal, no bleeding."
        ),
    },
    "de-DE": {
        "name": "German",
        "display": "Deutsch",
        "speech_locale": "de-DE",
        "example_dictation": (
            "Zahn 14, Taschentiefe 4 Millimeter mesial, Blutung bei Sondierung. "
            "Zahn 26, Rezession 2 Millimeter bukkal. "
            "Zahn 36, Taschentiefe 5 Millimeter distal, keine Blutung."
        ),
    },
    "cs-CZ": {
        "name": "Czech",
        "display": "Čeština",
        "speech_locale": "cs-CZ",
        "example_dictation": (
            "Zub 14, hloubka kapsy 4 milimetry mesiálně, krvácení při sondáži. "
            "Zub 26, recese 2 milimetry bukálně. "
            "Zub 36, hloubka kapsy 5 milimetrů distálně, bez krvácení."
        ),
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


def get_example_dictation(locale: str) -> str:
    """Get the example dictation text for a given locale."""
    return LANGUAGES.get(locale, LANGUAGES["en-US"])["example_dictation"]
