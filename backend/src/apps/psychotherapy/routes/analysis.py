"""
Psychotherapy tracker API routes.
"""

import base64

import msgspec
from litestar import Controller, get, post

from src.shared.azure_stt import transcribe_audio_continuous
from src.apps.psychotherapy.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    LanguageInfo,
    LanguagesResponse,
    MetricsResponse,
    MonologueInfo,
    ReportResponse,
    SessionResponse,
    SessionsResponse,
)
from src.apps.psychotherapy.services.analysis import analyze_monologue
from src.apps.psychotherapy.session_storage import get_session_count, get_sessions, store_session
from src.apps.psychotherapy.languages import LANGUAGES, MONOLOGUES


def _session_to_response(session_data: dict) -> SessionResponse:
    """Convert stored session dict to response schema."""
    metrics = session_data.get("metrics", {})
    report = session_data.get("report", {})
    return SessionResponse(
        metrics=MetricsResponse(
            anxiety=metrics.get("anxiety", 5),
            depression=metrics.get("depression", 5),
            stress=metrics.get("stress", 5),
            emotional_stability=metrics.get("emotional_stability", 5),
            positive_affect=metrics.get("positive_affect", 5),
            energy_level=metrics.get("energy_level", 5),
        ),
        report=ReportResponse(
            summary=report.get("summary", ""),
            key_emotions=report.get("key_emotions", ""),
            concerns_themes=report.get("concerns_themes", ""),
            insights=report.get("insights", ""),
        ),
        transcription=session_data.get("transcription", ""),
        session_number=session_data.get("session_number", 1),
        timestamp=session_data.get("timestamp", ""),
    )


class AnalysisController(Controller):
    path = "/api/psychotherapy"

    @post("/process")
    async def process_audio(self, data: AnalysisRequest) -> AnalysisResponse:
        """Process audio: transcribe and analyze monologue."""
        audio_data = base64.b64decode(data.audio_base64)

        session_number = get_session_count() + 1

        # Continuous recognition for longer monologues
        transcription = transcribe_audio_continuous(audio_data, data.locale)

        # Analyze the monologue
        result = analyze_monologue(transcription, session_number)

        # Store the session
        session_data = {
            "metrics": msgspec.to_builtins(result.metrics),
            "report": msgspec.to_builtins(result.report),
            "transcription": result.transcription,
            "timestamp": result.timestamp.isoformat(),
            "session_number": result.session_number,
        }
        store_session(session_data)

        return AnalysisResponse(
            session=_session_to_response(session_data),
            session_count=get_session_count(),
        )

    @get("/sessions")
    async def get_today_sessions(self) -> SessionsResponse:
        """Get all sessions for today."""
        sessions = get_sessions()
        return SessionsResponse(
            sessions=[_session_to_response(s) for s in sessions]
        )

    @get("/languages")
    async def get_languages(self) -> LanguagesResponse:
        """Get available languages with monologues."""
        return LanguagesResponse(
            languages=[
                LanguageInfo(
                    locale=locale,
                    name=info["name"],
                    display=info["display"],
                    monologues=[
                        MonologueInfo(id=key, title=val["title"], text=val["text"])
                        for key, val in MONOLOGUES.get(locale, {}).items()
                    ],
                )
                for locale, info in LANGUAGES.items()
            ]
        )
