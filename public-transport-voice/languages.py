"""
Language configuration for the voice translation application.
Contains 15 curated languages with their Azure Speech locale codes and neural voices.
"""

# Language configuration: locale -> (display name, neural voice name, translator code)
# - locale: Azure Speech SDK locale code (e.g., "en-US")
# - display name: Human-readable language name
# - neural voice: Azure TTS neural voice name
# - translator code: Azure Translator language code (usually just the language part)

LANGUAGES = {
    "en-US": {
        "name": "English (US)",
        "voice": "en-US-JennyNeural",
        "translator_code": "en",
    },
    "en-GB": {
        "name": "English (UK)",
        "voice": "en-GB-SoniaNeural",
        "translator_code": "en",
    },
    "es-ES": {
        "name": "Spanish (Spain)",
        "voice": "es-ES-ElviraNeural",
        "translator_code": "es",
    },
    "es-MX": {
        "name": "Spanish (Mexico)",
        "voice": "es-MX-DaliaNeural",
        "translator_code": "es",
    },
    "fr-FR": {
        "name": "French",
        "voice": "fr-FR-DeniseNeural",
        "translator_code": "fr",
    },
    "de-DE": {
        "name": "German",
        "voice": "de-DE-KatjaNeural",
        "translator_code": "de",
    },
    "it-IT": {
        "name": "Italian",
        "voice": "it-IT-ElsaNeural",
        "translator_code": "it",
    },
    "pt-BR": {
        "name": "Portuguese (Brazil)",
        "voice": "pt-BR-FranciscaNeural",
        "translator_code": "pt",
    },
    "zh-CN": {
        "name": "Chinese (Mandarin)",
        "voice": "zh-CN-XiaoxiaoNeural",
        "translator_code": "zh-Hans",
    },
    "ja-JP": {
        "name": "Japanese",
        "voice": "ja-JP-NanamiNeural",
        "translator_code": "ja",
    },
    "ko-KR": {
        "name": "Korean",
        "voice": "ko-KR-SunHiNeural",
        "translator_code": "ko",
    },
    "ru-RU": {
        "name": "Russian",
        "voice": "ru-RU-SvetlanaNeural",
        "translator_code": "ru",
    },
    "ar-SA": {
        "name": "Arabic",
        "voice": "ar-SA-ZariyahNeural",
        "translator_code": "ar",
    },
    "hi-IN": {
        "name": "Hindi",
        "voice": "hi-IN-SwaraNeural",
        "translator_code": "hi",
    },
    "pl-PL": {
        "name": "Polish",
        "voice": "pl-PL-AgnieszkaNeural",
        "translator_code": "pl",
    },
}


def get_language_options():
    """Return list of (locale, display_name) tuples for dropdown options."""
    return [(locale, info["name"]) for locale, info in LANGUAGES.items()]


def get_voice_for_locale(locale: str) -> str:
    """Get the neural voice name for a given locale."""
    return LANGUAGES.get(locale, {}).get("voice", "en-US-JennyNeural")


def get_translator_code(locale: str) -> str:
    """Get the translator language code for a given locale."""
    return LANGUAGES.get(locale, {}).get("translator_code", "en")


def get_language_name(locale: str) -> str:
    """Get the display name for a given locale."""
    return LANGUAGES.get(locale, {}).get("name", locale)
