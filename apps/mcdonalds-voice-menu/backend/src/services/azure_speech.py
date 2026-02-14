import json
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from src.settings import get_settings

_LANGUAGE_NAME_FIELDS = {
    "en-US": "name",
    "de-DE": "name_de",
    "cs-CZ": "name_cs",
}

_menu_phrases: dict[str, list[str]] = {}


def _load_menu_phrases() -> dict[str, list[str]]:
    """Load menu item names per language from menu_items.json (cached)."""
    if _menu_phrases:
        return _menu_phrases
    menu_path = Path(__file__).resolve().parents[2] / "data" / "menu_items.json"
    items = json.loads(menu_path.read_text(encoding="utf-8"))
    for lang, field in _LANGUAGE_NAME_FIELDS.items():
        _menu_phrases[lang] = list({item[field] for item in items})
    return _menu_phrases


async def transcribe_audio(audio_data: bytes, language: str = "en-US") -> str:
    """Transcribe audio using Azure Speech-to-Text"""
    settings = get_settings()

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.AZURE_SPEECH_KEY,
        region=settings.AZURE_SPEECH_REGION
    )
    speech_config.speech_recognition_language = language

    # Use push stream for audio data
    stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Add menu item names as phrase hints to improve recognition accuracy
    phrases = _load_menu_phrases().get(language, _load_menu_phrases().get("en-US", []))
    phrase_list = speechsdk.PhraseListGrammar.from_recognizer(recognizer)
    for phrase in phrases:
        phrase_list.addPhrase(phrase)

    stream.write(audio_data)
    stream.close()

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    else:
        raise Exception(f"Speech recognition failed: {result.reason}")