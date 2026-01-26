"""
Session storage for psychotherapy tracker.
Stores sessions in memory for the current browser session.
Uses a simple in-memory store (resets on server restart).
"""

from datetime import date
from typing import Optional

# In-memory storage: {date_str: [session_dicts]}
_sessions: dict[str, list[dict]] = {}


def _get_today() -> str:
    """Get today's date as a string."""
    return date.today().isoformat()


def store_session(session_data: dict) -> int:
    """
    Store a session.

    Args:
        session_data: Session data including metrics and report

    Returns:
        Session number for today (1-indexed)
    """
    today = _get_today()

    if today not in _sessions:
        _sessions[today] = []

    session_number = len(_sessions[today]) + 1
    session_data["session_number"] = session_number

    _sessions[today].append(session_data)

    return session_number


def get_sessions() -> list[dict]:
    """
    Get all sessions for today.

    Returns:
        List of session data dictionaries
    """
    today = _get_today()
    return _sessions.get(today, [])


def get_session_count() -> int:
    """
    Get the number of sessions for today.

    Returns:
        Number of sessions today
    """
    return len(get_sessions())


def get_latest_session() -> Optional[dict]:
    """
    Get the latest session for today.

    Returns:
        Latest session data or None if no sessions
    """
    sessions = get_sessions()
    if sessions:
        return sessions[-1]
    return None


def clear_sessions() -> None:
    """Clear all sessions (for testing)."""
    global _sessions
    _sessions = {}
