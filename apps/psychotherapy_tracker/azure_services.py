"""
Azure service wrappers for the Psychotherapy Tracker application.
Handles Speech-to-Text and OpenAI analysis.
"""

import json
import os
import time

import azure.cognitiveservices.speech as speechsdk
from openai import OpenAI
from dotenv import load_dotenv

from data_models import PsychMetrics, AnalysisReport, SessionResult

load_dotenv()


class AzureServiceError(Exception):
    """Custom exception for Azure service errors."""

    pass


# System prompt for psychological analysis
SYSTEM_PROMPT = """You are a supportive psychological wellness assistant analyzing voice monologues. Your role is to provide helpful insights while being empathetic and non-judgmental.

## Your Task
Analyze the transcribed monologue and provide:
1. Six psychological metrics (rated 1-10)
2. A structured wellness report

## Metrics (rate each 1-10)
- **anxiety**: Level of anxiety/worry expressed (1=calm, 10=highly anxious)
- **depression**: Depressive indicators present (1=none, 10=severe)
- **stress**: Stress level indicated (1=relaxed, 10=highly stressed)
- **emotional_stability**: Emotional regulation shown (1=unstable, 10=very stable)
- **positive_affect**: Positive emotions/outlook (1=none, 10=very positive)
- **energy_level**: Vitality/energy expressed (1=exhausted, 10=energetic)

## Report Sections
- **summary**: 2-3 sentences summarizing the overall emotional state
- **key_emotions**: List the main emotions identified (comma-separated)
- **concerns_themes**: Main concerns or recurring themes mentioned
- **insights**: Helpful observations and gentle suggestions (supportive tone)

## Guidelines
- Be warm, supportive, and non-clinical in tone
- Focus on what the person expressed, not diagnoses
- Offer hope and validation
- Keep report sections concise (2-4 sentences each)
- Base metrics only on what was actually expressed

## Output Format
Return ONLY valid JSON matching this schema:
{
  "metrics": {
    "anxiety": <1-10>,
    "depression": <1-10>,
    "stress": <1-10>,
    "emotional_stability": <1-10>,
    "positive_affect": <1-10>,
    "energy_level": <1-10>
  },
  "report": {
    "summary": "<string>",
    "key_emotions": "<string>",
    "concerns_themes": "<string>",
    "insights": "<string>"
  }
}

Now analyze the following monologue and return ONLY the JSON response:"""


def transcribe_audio(audio_data: bytes, locale: str = "en-US") -> str:
    """
    Transcribe audio data using Azure Speech-to-Text with continuous recognition.

    Args:
        audio_data: Audio data in WAV format (16kHz, 16-bit, mono)
        locale: Language locale code (e.g., "en-US", "de-DE", "cs-CZ")

    Returns:
        Transcribed text

    Raises:
        AzureServiceError: If transcription fails
    """
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION", "westeurope")

    if not speech_key:
        raise AzureServiceError("Azure Speech Key not configured")

    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=speech_region
        )
        speech_config.speech_recognition_language = locale

        # Create push stream and audio config
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # Collect results using continuous recognition
        results: list[str] = []
        done = False

        def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs) -> None:
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                results.append(evt.result.text)

        def canceled_cb(evt: speechsdk.SpeechRecognitionCanceledEventArgs) -> None:
            nonlocal done
            done = True

        def stopped_cb(evt: speechsdk.SessionEventArgs) -> None:
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


def get_openai_client() -> OpenAI:
    """Create and return OpenAI client configured for Azure AI Foundry."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")

    if not endpoint or not api_key:
        raise AzureServiceError("Azure OpenAI credentials not configured")

    # Azure AI Foundry uses the standard OpenAI client with base_url
    base_url = endpoint.rstrip("/")
    if not base_url.endswith("/openai/v1"):
        base_url = f"{base_url}/openai/v1"

    return OpenAI(
        base_url=base_url,
        api_key=api_key,
    )


def analyze_monologue(transcription: str, session_number: int) -> SessionResult:
    """
    Analyze a transcribed monologue using Azure OpenAI.

    Args:
        transcription: The transcribed text from speech recognition
        session_number: The session number for today

    Returns:
        SessionResult object with metrics, report, and metadata

    Raises:
        AzureServiceError: If analysis fails
    """
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

    if not transcription.strip():
        raise AzureServiceError("No transcription provided")

    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcription},
            ],
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content
        if not result_text:
            raise AzureServiceError("Empty response from LLM")

        # Parse JSON response
        result_data = json.loads(result_text)

        # Validate and create Pydantic models
        metrics = PsychMetrics(**result_data.get("metrics", {}))
        report = AnalysisReport(**result_data.get("report", {}))

        return SessionResult(
            metrics=metrics,
            report=report,
            transcription=transcription,
            session_number=session_number,
        )

    except json.JSONDecodeError as e:
        raise AzureServiceError(f"Failed to parse LLM response as JSON: {str(e)}")
    except AzureServiceError:
        raise
    except Exception as e:
        raise AzureServiceError(f"Analysis failed: {str(e)}")


def process_recording(
    audio_data: bytes, locale: str, session_number: int
) -> SessionResult:
    """
    Process a voice recording: transcribe and analyze.

    Args:
        audio_data: WAV audio data
        locale: Language locale
        session_number: Session number for today

    Returns:
        SessionResult with full analysis
    """
    # Step 1: Transcribe
    transcription = transcribe_audio(audio_data, locale)

    # Step 2: Analyze
    result = analyze_monologue(transcription, session_number)

    return result
