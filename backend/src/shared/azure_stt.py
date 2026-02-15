"""
Azure Speech-to-Text service wrappers.
Provides one-shot and continuous recognition.
"""

import io
import time
import wave

import azure.cognitiveservices.speech as speechsdk

from src.settings import get_settings


class AzureServiceError(Exception):
    """Custom exception for Azure service errors."""

    pass


def transcribe_audio(audio_data: bytes, locale: str = "en-US") -> str:
    """
    Transcribe audio data using Azure Speech-to-Text (one-shot recognition).

    Args:
        audio_data: Audio data in WAV format (16kHz, 16-bit, mono)
        locale: Language locale code (e.g., "en-US")

    Returns:
        Transcribed text

    Raises:
        AzureServiceError: If transcription fails
    """
    settings = get_settings()
    if not settings.AZURE_SPEECH_KEY:
        raise AzureServiceError("Azure Speech Key not configured")

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY, region=settings.AZURE_SPEECH_REGION
        )
        speech_config.speech_recognition_language = locale

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        if audio_data[:4] == b'RIFF':
            with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
                audio_data = wav_file.readframes(wav_file.getnframes())

        audio_stream.write(audio_data)
        audio_stream.close()

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


def transcribe_audio_continuous(audio_data: bytes, locale: str = "en-US") -> str:
    """
    Transcribe longer audio using continuous recognition.
    Better for recordings longer than 15 seconds.

    Args:
        audio_data: Audio data in WAV format (16kHz, 16-bit, mono)
        locale: Language locale code

    Returns:
        Transcribed text (concatenated from all recognized segments)

    Raises:
        AzureServiceError: If transcription fails
    """
    settings = get_settings()
    if not settings.AZURE_SPEECH_KEY:
        raise AzureServiceError("Azure Speech Key not configured")

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY, region=settings.AZURE_SPEECH_REGION
        )
        speech_config.speech_recognition_language = locale

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        results: list[str] = []
        done = False

        def recognized_cb(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                results.append(evt.result.text)

        def canceled_cb(evt):
            nonlocal done
            done = True

        def stopped_cb(evt):
            nonlocal done
            done = True

        recognizer.recognized.connect(recognized_cb)
        recognizer.canceled.connect(canceled_cb)
        recognizer.session_stopped.connect(stopped_cb)

        recognizer.start_continuous_recognition()

        if audio_data[:4] == b'RIFF':
            with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
                audio_data = wav_file.readframes(wav_file.getnframes())

        audio_stream.write(audio_data)
        audio_stream.close()

        timeout = 60
        start = time.time()
        while not done and (time.time() - start) < timeout:
            time.sleep(0.1)

        recognizer.stop_continuous_recognition()

        if not results:
            raise AzureServiceError("No speech could be recognized in the audio")

        return " ".join(results)

    except AzureServiceError:
        raise
    except Exception as e:
        raise AzureServiceError(f"Speech-to-Text error: {str(e)}")
