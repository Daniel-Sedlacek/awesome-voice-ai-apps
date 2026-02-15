"""
Msgspec models for psychotherapy tracking data.
"""

from datetime import datetime
from typing import Annotated

import msgspec
from msgspec import Meta, Struct


class PsychMetrics(Struct):
    """Six psychological metrics rated 1-10."""
    anxiety: Annotated[int, Meta(ge=1, le=10, description="Anxiety level (1=low, 10=high)")]
    depression: Annotated[int, Meta(ge=1, le=10, description="Depression indicators (1=low, 10=high)")]
    stress: Annotated[int, Meta(ge=1, le=10, description="Stress level (1=low, 10=high)")]
    emotional_stability: Annotated[int, Meta(ge=1, le=10, description="Emotional stability (1=low, 10=high)")]
    positive_affect: Annotated[int, Meta(ge=1, le=10, description="Positive emotions (1=low, 10=high)")]
    energy_level: Annotated[int, Meta(ge=1, le=10, description="Energy/vitality (1=low, 10=high)")]


class AnalysisReport(Struct):
    """Structured psychological analysis report."""
    summary: Annotated[str, Meta(description="Brief overall summary")]
    key_emotions: Annotated[str, Meta(description="Main emotions identified")]
    concerns_themes: Annotated[str, Meta(description="Recurring concerns or themes")]
    insights: Annotated[str, Meta(description="Psychological insights and observations")]


class SessionResult(Struct):
    """Complete session result with metrics, report, and metadata."""
    metrics: Annotated[PsychMetrics, Meta(description="Psychological metrics for the session")]
    report: Annotated[AnalysisReport, Meta(description="Structured analysis report")]
    transcription: Annotated[str, Meta(description="Original transcribed text")]
    session_number: Annotated[int, Meta(description="Session number for today")]
    timestamp: datetime = msgspec.field(default_factory=datetime.utcnow)


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

METRIC_COLORS = {
    "anxiety": "#EF4444",
    "depression": "#6366F1",
    "stress": "#F59E0B",
    "emotional_stability": "#10B981",
    "positive_affect": "#EC4899",
    "energy_level": "#8B5CF6",
}
