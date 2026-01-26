"""
Pydantic models for psychotherapy tracking data.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PsychMetrics(BaseModel):
    """Six psychological metrics rated 1-10."""

    anxiety: int = Field(..., ge=1, le=10, description="Anxiety level (1=low, 10=high)")
    depression: int = Field(
        ..., ge=1, le=10, description="Depression indicators (1=low, 10=high)"
    )
    stress: int = Field(..., ge=1, le=10, description="Stress level (1=low, 10=high)")
    emotional_stability: int = Field(
        ..., ge=1, le=10, description="Emotional stability (1=low, 10=high)"
    )
    positive_affect: int = Field(
        ..., ge=1, le=10, description="Positive emotions (1=low, 10=high)"
    )
    energy_level: int = Field(
        ..., ge=1, le=10, description="Energy/vitality (1=low, 10=high)"
    )


class AnalysisReport(BaseModel):
    """Structured psychological analysis report."""

    summary: str = Field(..., description="Brief overall summary")
    key_emotions: str = Field(..., description="Main emotions identified")
    concerns_themes: str = Field(..., description="Recurring concerns or themes")
    insights: str = Field(..., description="Psychological insights and observations")


class SessionResult(BaseModel):
    """Complete session result with metrics, report, and metadata."""

    metrics: PsychMetrics
    report: AnalysisReport
    transcription: str = Field(..., description="Original transcribed text")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_number: int = Field(..., description="Session number for today")


# Metric display names for each language
METRIC_NAMES = {
    "en-US": {
        "anxiety": "Anxiety",
        "depression": "Depression",
        "stress": "Stress",
        "emotional_stability": "Stability",
        "positive_affect": "Positivity",
        "energy_level": "Energy",
    },
    "de-DE": {
        "anxiety": "Angst",
        "depression": "Depression",
        "stress": "Stress",
        "emotional_stability": "Stabilität",
        "positive_affect": "Positivität",
        "energy_level": "Energie",
    },
    "cs-CZ": {
        "anxiety": "Úzkost",
        "depression": "Deprese",
        "stress": "Stres",
        "emotional_stability": "Stabilita",
        "positive_affect": "Pozitivita",
        "energy_level": "Energie",
    },
}

# Metric colors for charts
METRIC_COLORS = {
    "anxiety": "#EF4444",  # Red
    "depression": "#6366F1",  # Indigo
    "stress": "#F59E0B",  # Amber
    "emotional_stability": "#10B981",  # Emerald
    "positive_affect": "#EC4899",  # Pink
    "energy_level": "#8B5CF6",  # Purple
}
