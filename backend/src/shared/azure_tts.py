"""
Azure Text-to-Speech service wrapper.
"""

import base64

import azure.cognitiveservices.speech as speechsdk

from src.settings import get_settings
from src.shared.azure_stt import AzureServiceError


def synthesize_speech(text: str, voice_name: str) -> bytes:
    """
    Synthesize speech from text using Azure Text-to-Speech.

    Args:
        text: Text to synthesize
        voice_name: Azure TTS neural voice name (e.g., "en-US-JennyNeural")

    Returns:
        Audio data in WAV format

    Raises:
        AzureServiceError: If synthesis fails
    """
    settings = get_settings()
    if not settings.AZURE_SPEECH_KEY:
        raise AzureServiceError("Azure Speech Key not configured")

    if not text.strip():
        raise AzureServiceError("No text provided for synthesis")

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY, region=settings.AZURE_SPEECH_REGION
        )
        speech_config.speech_synthesis_voice_name = voice_name
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
        )

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=None
        )

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
    """Convert audio data to base64 string."""
    return base64.b64encode(audio_data).decode("utf-8")
