from dataclasses import dataclass, field
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo


@dataclass
class UserSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    language: str = "en-US"
    conversation_history: list[dict] = field(default_factory=list)
    accumulated_criteria: str = ""
    displayed_item_ids: list[int] = field(default_factory=list)
    basket_item_ids: list[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

    def add_utterance(self, text: str, intent: str, new_search: bool = False):
        """Add a user utterance to the conversation history."""
        self.conversation_history.append({
            "text": text,
            "intent": intent,
            "timestamp": datetime.now(ZoneInfo("UTC")).isoformat()
        })
        if intent == "ADD":
            if new_search:
                self.accumulated_criteria = text
                self.displayed_item_ids = []
            else:
                self.accumulated_criteria = f"{self.accumulated_criteria} {text}".strip()

    def add_to_basket(self, item_ids: list[int]):
        """Add items to basket, avoiding duplicates."""
        for item_id in item_ids:
            if item_id not in self.basket_item_ids:
                self.basket_item_ids.append(item_id)

    def remove_from_basket(self, item_ids: list[int]):
        """Remove items from basket."""
        self.basket_item_ids = [
            id for id in self.basket_item_ids
            if id not in item_ids
        ]

    def clear(self):
        self.accumulated_criteria = ""
        self.displayed_item_ids = []
        self.basket_item_ids = []
        # Keep conversation history for context


# In-memory session store (good enough for demo)
sessions: dict[str, UserSession] = {}


def get_or_create_session(session_id: str | None = None) -> UserSession:
    """Get existing session or create a new one."""
    if session_id and session_id in sessions:
        return sessions[session_id]

    session = UserSession()
    sessions[session.session_id] = session
    return session
