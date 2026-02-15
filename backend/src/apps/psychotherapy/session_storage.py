"""
Session storage for psychotherapy tracker.
In-memory store (resets on server restart).
"""

from datetime import date


_sessions: dict[str, list[dict]] = {}


def _get_today() -> str:
    """Get today's date as a string."""
    return date.today().isoformat()


def store_session(session_data: dict) -> int:
    """
    Store a session and return session number for today (1-indexed).
    """
    today = _get_today()

    if today not in _sessions:
        _sessions[today] = []

    session_number = len(_sessions[today]) + 1
    session_data["session_number"] = session_number

    _sessions[today].append(session_data)

    return session_number


def get_sessions() -> list[dict]:
    """Get all sessions for today."""
    today = _get_today()
    return _sessions.get(today, [])


def get_session_count() -> int:
    """Get the number of sessions for today."""
    return len(get_sessions())
