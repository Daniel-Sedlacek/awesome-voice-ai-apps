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
    basket_quantities: dict[int, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

    def add_utterance(self, text: str, intent: str, new_search: bool = False, search_criteria: str | None = None):
        """Add a user utterance to the conversation history."""
        self.conversation_history.append({
            "text": text,
            "intent": intent,
            "timestamp": datetime.now(ZoneInfo("UTC")).isoformat()
        })
        if intent == "ADD":
            criteria = search_criteria or text
            if new_search:
                self.accumulated_criteria = criteria
                self.displayed_item_ids = []
            else:
                self.accumulated_criteria = f"{self.accumulated_criteria} {criteria}".strip()

    def add_to_basket(self, item_ids: list[int]):
        """Add items to basket, incrementing quantity if already present."""
        for item_id in item_ids:
            if item_id not in self.basket_item_ids:
                self.basket_item_ids.append(item_id)
                self.basket_quantities[item_id] = 1
            else:
                self.basket_quantities[item_id] = self.basket_quantities.get(item_id, 1) + 1

    def remove_from_basket(self, item_ids: list[int]):
        """Remove items from basket (removes entirely regardless of quantity)."""
        self.basket_item_ids = [
            id for id in self.basket_item_ids
            if id not in item_ids
        ]
        for item_id in item_ids:
            self.basket_quantities.pop(item_id, None)

    def clear(self):
        self.accumulated_criteria = ""
        self.displayed_item_ids = []
        self.basket_item_ids = []
        self.basket_quantities = {}
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
