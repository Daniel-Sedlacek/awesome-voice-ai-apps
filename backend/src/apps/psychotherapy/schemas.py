"""
Request/response schemas for the psychotherapy tracker app.
"""

import msgspec


class AnalysisRequest(msgspec.Struct):
    """Audio analysis request."""
    audio_base64: str
    locale: str = "en-US"


class MetricsResponse(msgspec.Struct):
    """Psychological metrics."""
    anxiety: int
    depression: int
    stress: int
    emotional_stability: int
    positive_affect: int
    energy_level: int


class ReportResponse(msgspec.Struct):
    """Analysis report."""
    summary: str
    key_emotions: str
    concerns_themes: str
    insights: str


class SessionResponse(msgspec.Struct):
    """Single session result."""
    metrics: MetricsResponse
    report: ReportResponse
    transcription: str
    session_number: int
    timestamp: str


class AnalysisResponse(msgspec.Struct):
    """Full analysis response."""
    session: SessionResponse
    session_count: int


class SessionsResponse(msgspec.Struct):
    """Today's sessions."""
    sessions: list[SessionResponse]


class MonologueInfo(msgspec.Struct):
    """Monologue info for frontend."""
    id: str
    title: str
    text: str


class LanguageInfo(msgspec.Struct):
    """Language info for frontend."""
    locale: str
    name: str
    display: str
    monologues: list[MonologueInfo]


class LanguagesResponse(msgspec.Struct):
    """Languages with monologues."""
    languages: list[LanguageInfo]
