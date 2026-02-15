"""
Azure OpenAI service for analyzing psychotherapy monologues.
"""

import json

from src.shared.azure_openai import get_openai_client
from src.settings import get_settings
from src.apps.psychotherapy.data_models import PsychMetrics, AnalysisReport, SessionResult


class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    pass


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


def analyze_monologue(transcription: str, session_number: int) -> SessionResult:
    """
    Analyze a transcribed monologue using Azure OpenAI.

    Args:
        transcription: The transcribed text from speech recognition
        session_number: The session number for today

    Returns:
        SessionResult object with metrics, report, and metadata

    Raises:
        AnalysisError: If analysis fails
    """
    if not transcription.strip():
        raise AnalysisError("No transcription provided")

    settings = get_settings()

    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcription},
            ],
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content
        if not result_text:
            raise AnalysisError("Empty response from LLM")

        result_data = json.loads(result_text)

        metrics = PsychMetrics(**result_data.get("metrics", {}))
        report = AnalysisReport(**result_data.get("report", {}))

        return SessionResult(
            metrics=metrics,
            report=report,
            transcription=transcription,
            session_number=session_number,
        )

    except json.JSONDecodeError as e:
        raise AnalysisError(f"Failed to parse LLM response as JSON: {str(e)}")
    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(f"Analysis failed: {str(e)}")
