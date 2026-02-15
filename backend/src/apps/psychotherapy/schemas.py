"""
Request/response schemas for the psychotherapy tracker app.
"""

from typing import Annotated

import msgspec
from msgspec import Meta


class AnalysisRequest(msgspec.Struct):
    """Audio analysis request."""
    audio_base64: Annotated[str, Meta(min_length=1, description="Base64-encoded audio data")]
    locale: Annotated[str, Meta(description="Speech recognition locale code")] = "en-US"


class MetricsResponse(msgspec.Struct):
    """Psychological metrics."""
    anxiety: Annotated[int, Meta(ge=1, le=10, description="Anxiety level (1=low, 10=high)")]
    depression: Annotated[int, Meta(ge=1, le=10, description="Depression indicators (1=low, 10=high)")]
    stress: Annotated[int, Meta(ge=1, le=10, description="Stress level (1=low, 10=high)")]
    emotional_stability: Annotated[int, Meta(ge=1, le=10, description="Emotional stability (1=low, 10=high)")]
    positive_affect: Annotated[int, Meta(ge=1, le=10, description="Positive emotions (1=low, 10=high)")]
    energy_level: Annotated[int, Meta(ge=1, le=10, description="Energy/vitality (1=low, 10=high)")]


class ReportResponse(msgspec.Struct):
    """Analysis report."""
    summary: Annotated[str, Meta(description="Brief overall summary")]
    key_emotions: Annotated[str, Meta(description="Main emotions identified")]
    concerns_themes: Annotated[str, Meta(description="Recurring concerns or themes")]
    insights: Annotated[str, Meta(description="Psychological insights and observations")]


class SessionResponse(msgspec.Struct):
    """Single session result."""
    metrics: Annotated[MetricsResponse, Meta(description="Psychological metrics for the session")]
    report: Annotated[ReportResponse, Meta(description="Structured analysis report")]
    transcription: Annotated[str, Meta(description="Speech-to-text transcription")]
    session_number: Annotated[int, Meta(ge=1, description="Session number for today")]
    timestamp: Annotated[str, Meta(description="ISO 8601 timestamp of the session")]


class AnalysisResponse(msgspec.Struct):
    """Full analysis response."""
    session: Annotated[SessionResponse, Meta(description="Current session result")]
    session_count: Annotated[int, Meta(ge=0, description="Total sessions today")]


class SessionsResponse(msgspec.Struct):
    """Today's sessions."""
    sessions: Annotated[list[SessionResponse], Meta(description="List of today's sessions")]


class MonologueInfo(msgspec.Struct):
    """Monologue info for frontend."""
    id: Annotated[str, Meta(description="Monologue identifier")]
    title: Annotated[str, Meta(description="Display title")]
    text: Annotated[str, Meta(description="Monologue text content")]


class LanguageInfo(msgspec.Struct):
    """Language info for frontend."""
    locale: Annotated[str, Meta(description="Language locale code")]
    name: Annotated[str, Meta(description="Language name")]
    display: Annotated[str, Meta(description="Display label for the UI")]
    monologues: Annotated[list[MonologueInfo], Meta(description="Available monologues for this language")]


class LanguagesResponse(msgspec.Struct):
    """Languages with monologues."""
    languages: Annotated[list[LanguageInfo], Meta(description="Available languages with monologues")]
