"""
Translation pipeline: STT -> Translate -> TTS for transport app.
"""

from src.shared.azure_stt import transcribe_audio, AzureServiceError
from src.shared.azure_tts import synthesize_speech, audio_to_base64
from src.shared.azure_translator import translate_text
from src.apps.transport.languages import get_voice_for_locale, get_translator_code


def process_recording(
    audio_data: bytes, source_locale: str, target_locale_1: str, target_locale_2: str
) -> dict:
    """
    Process a recording: transcribe, translate, and synthesize.

    Args:
        audio_data: Audio data in WAV format
        source_locale: Source language locale
        target_locale_1: First target language locale
        target_locale_2: Second target language locale

    Returns:
        Dict with original, translation_1, translation_2 (each with locale, text, audio_base64)
    """
    # Step 1: Transcribe the audio
    original_text = transcribe_audio(audio_data, source_locale)

    if not original_text.strip():
        raise AzureServiceError("No speech was recognized in the recording")

    # Step 2: Translate to target languages
    source_lang = get_translator_code(source_locale)
    target_lang_1 = get_translator_code(target_locale_1)
    target_lang_2 = get_translator_code(target_locale_2)

    translation_1 = translate_text(original_text, source_lang, target_lang_1)
    translation_2 = translate_text(original_text, source_lang, target_lang_2)

    # Step 3: Synthesize all three texts
    audio_original = synthesize_speech(original_text, get_voice_for_locale(source_locale))
    audio_translation_1 = synthesize_speech(translation_1, get_voice_for_locale(target_locale_1))
    audio_translation_2 = synthesize_speech(translation_2, get_voice_for_locale(target_locale_2))

    return {
        "original": {
            "locale": source_locale,
            "text": original_text,
            "audio_base64": audio_to_base64(audio_original),
        },
        "translation_1": {
            "locale": target_locale_1,
            "text": translation_1,
            "audio_base64": audio_to_base64(audio_translation_1),
        },
        "translation_2": {
            "locale": target_locale_2,
            "text": translation_2,
            "audio_base64": audio_to_base64(audio_translation_2),
        },
    }
