import azure.cognitiveservices.speech as speechsdk
from src.config import get_settings


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

    stream.write(audio_data)
    stream.close()

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    else:
        raise Exception(f"Speech recognition failed: {result.reason}")