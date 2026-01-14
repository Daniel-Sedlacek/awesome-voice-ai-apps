"""
Azure service wrappers for Speech-to-Text, Text-to-Speech, and Translation.
"""

import os
import io
import base64
import uuid
import requests
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from languages import get_voice_for_locale, get_translator_code

# Load environment variables
load_dotenv()

# Azure Speech Service configuration
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "westeurope")

# Azure Translator configuration
TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY", "")
TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION", "westeurope")
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"


class AzureServiceError(Exception):
    """Custom exception for Azure service errors."""

    pass


def transcribe_audio(audio_data: bytes, locale: str = "en-US") -> str:
    """
    Transcribe audio data using Azure Speech-to-Text.

    Args:
        audio_data: Audio data in WAV format (16kHz, 16-bit, mono)
        locale: Language locale code (e.g., "en-US")

    Returns:
        Transcribed text

    Raises:
        AzureServiceError: If transcription fails
    """
    if not SPEECH_KEY:
        raise AzureServiceError("Azure Speech Key not configured")

    try:
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, region=SPEECH_REGION
        )
        speech_config.speech_recognition_language = locale

        # Create audio config from the audio data
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        # Create recognizer
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # Push audio data to the stream
        audio_stream.write(audio_data)
        audio_stream.close()

        # Recognize speech
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise AzureServiceError("No speech could be recognized in the audio")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise AzureServiceError(f"Speech recognition canceled: {cancellation.reason}")
        else:
            raise AzureServiceError(f"Unexpected result: {result.reason}")

    except AzureServiceError:
        raise
    except Exception as e:
        raise AzureServiceError(f"Speech-to-Text error: {str(e)}")


def translate_text(text: str, source_locale: str, target_locale: str) -> str:
    """
    Translate text using Azure Translator.

    Args:
        text: Text to translate
        source_locale: Source language locale (e.g., "en-US")
        target_locale: Target language locale (e.g., "es-ES")

    Returns:
        Translated text

    Raises:
        AzureServiceError: If translation fails
    """
    if not TRANSLATOR_KEY:
        raise AzureServiceError("Azure Translator Key not configured")

    if not text.strip():
        return ""

    # Get translator language codes
    source_lang = get_translator_code(source_locale)
    target_lang = get_translator_code(target_locale)

    # If source and target are the same, return original text
    if source_lang == target_lang:
        return text

    try:
        url = f"{TRANSLATOR_ENDPOINT}/translate"
        params = {
            "api-version": "3.0",
            "from": source_lang,
            "to": target_lang,
        }
        headers = {
            "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
            "Content-Type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        body = [{"text": text}]

        response = requests.post(url, params=params, headers=headers, json=body, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result and len(result) > 0 and "translations" in result[0]:
            return result[0]["translations"][0]["text"]
        else:
            raise AzureServiceError("Unexpected translation response format")

    except requests.exceptions.RequestException as e:
        raise AzureServiceError(f"Translation request failed: {str(e)}")
    except (KeyError, IndexError) as e:
        raise AzureServiceError(f"Failed to parse translation response: {str(e)}")


def synthesize_speech(text: str, locale: str = "en-US") -> bytes:
    """
    Synthesize speech from text using Azure Text-to-Speech.

    Args:
        text: Text to synthesize
        locale: Language locale code (e.g., "en-US")

    Returns:
        Audio data in WAV format

    Raises:
        AzureServiceError: If synthesis fails
    """
    if not SPEECH_KEY:
        raise AzureServiceError("Azure Speech Key not configured")

    if not text.strip():
        raise AzureServiceError("No text provided for synthesis")

    try:
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, region=SPEECH_REGION
        )

        # Set the voice
        voice_name = get_voice_for_locale(locale)
        speech_config.speech_synthesis_voice_name = voice_name

        # Set output format to WAV
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
        )

        # Create synthesizer with no audio output (we'll capture the data)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=None
        )

        # Synthesize
        result = synthesizer.speak_text(text)

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise AzureServiceError(f"Speech synthesis canceled: {cancellation.reason}")
        else:
            raise AzureServiceError(f"Unexpected result: {result.reason}")

    except AzureServiceError:
        raise
    except Exception as e:
        raise AzureServiceError(f"Text-to-Speech error: {str(e)}")


def audio_to_base64(audio_data: bytes) -> str:
    """
    Convert audio data to base64 string for embedding in HTML.

    Args:
        audio_data: Audio data in WAV format

    Returns:
        Base64-encoded string
    """
    return base64.b64encode(audio_data).decode("utf-8")


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
        Dict with transcription, translations, and audio data

    Raises:
        AzureServiceError: If any step fails
    """
    # Step 1: Transcribe the audio
    original_text = transcribe_audio(audio_data, source_locale)

    if not original_text.strip():
        raise AzureServiceError("No speech was recognized in the recording")

    # Step 2: Translate to target languages
    translation_1 = translate_text(original_text, source_locale, target_locale_1)
    translation_2 = translate_text(original_text, source_locale, target_locale_2)

    # Step 3: Synthesize all three texts
    audio_original = synthesize_speech(original_text, source_locale)
    audio_translation_1 = synthesize_speech(translation_1, target_locale_1)
    audio_translation_2 = synthesize_speech(translation_2, target_locale_2)

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
