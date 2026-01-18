"""
Azure Speech-to-Text service wrapper for dental dictation.
"""

import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure Speech Service configuration
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "westeurope")


class AzureServiceError(Exception):
    """Custom exception for Azure service errors."""
    pass


def transcribe_audio(audio_data: bytes, locale: str = "en-US") -> str:
    """
    Transcribe audio data using Azure Speech-to-Text.

    Args:
        audio_data: Audio data in WAV format (16kHz, 16-bit, mono)
        locale: Language locale code (e.g., "en-US", "de-DE", "cs-CZ")

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
    if not SPEECH_KEY:
        raise AzureServiceError("Azure Speech Key not configured")

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, region=SPEECH_REGION
        )
        speech_config.speech_recognition_language = locale

        # Create push stream and audio config
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # Collect results
        results = []
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

        # Start continuous recognition
        recognizer.start_continuous_recognition()

        # Push audio data
        audio_stream.write(audio_data)
        audio_stream.close()

        # Wait for recognition to complete
        import time
        timeout = 60  # Max 60 seconds
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
