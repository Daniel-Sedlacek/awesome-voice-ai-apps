import base64
import time

from litestar import Controller, post
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas import (
    AudioRequest,
    AudioResponse,
    BasketActionRequest,
    BasketActionResponse,
    menu_item_to_response,
)
from src.session import get_or_create_session
from src.services.azure_speech import transcribe_audio
from src.services.azure_openai import parse_intent
from src.services.embeddings import create_query_embedding
from src.services.retrieval import (
    search_menu_items,
    get_items_by_ids,
    get_item_ids_by_names,
    get_item_ids_by_names_from_set,
)


class PipelineTimer:
    """Collects step durations and prints a one-line summary."""

    def __init__(self):
        self._steps: list[tuple[str, float]] = []
        self._last = time.perf_counter()
        self._start = self._last

    def mark(self, name: str):
        now = time.perf_counter()
        self._steps.append((name, now - self._last))
        self._last = now

    def log(self):
        total = time.perf_counter() - self._start
        parts = " | ".join(f"{name}: {dur * 1000:.0f}ms" for name, dur in self._steps)
        print(f"\n{'=' * 60}")
        print(f"  Pipeline Timing")
        print(f"  {parts}")
        print(f"  Total: {total * 1000:.0f}ms")
        print(f"{'=' * 60}\n")


class AudioController(Controller):
    path = "/api"
    dependencies = {"db": Provide(get_db_session)}

    @post("/process-audio")
    async def process_audio(
        self,
        data: AudioRequest,
        db: AsyncSession,
    ) -> AudioResponse:
        """
        Process audio and return matching menu items.

        1. Transcribe audio
        2. Parse intent with LLM
        3. Based on intent, search/modify results
        4. Return menu items + basket
        """
        timer = PipelineTimer()
        session = get_or_create_session(data.session_id)
        session.language = data.language

        # Transcribe audio
        audio_bytes = base64.b64decode(data.audio_base64)
        transcript = await transcribe_audio(audio_bytes, session.language)
        timer.mark("STT")

        if not transcript:
            timer.log()
            basket_items_db = await get_items_by_ids(db, session.basket_item_ids)
            return AudioResponse(
                transcript="",
                message="No speech was recognized in the recording",
                session_id=session.session_id,
                basket_items=[menu_item_to_response(i) for i in basket_items_db],
            )

        # Parse intent
        intent_result = await parse_intent(transcript, session.conversation_history)
        intent = intent_result.get("intent")
        timer.mark("LLM")
        msg = ""

        if intent == "CLEAR":
            timer.log()
            session.clear()
            return AudioResponse(
                transcript=transcript,
                message="Order cleared. Start fresh!",
                session_id=session.session_id,
            )

        elif intent == "REMOVE":
            remove_names = intent_result.get("remove_items", [])
            removed_ids = await get_item_ids_by_names(db, remove_names)
            session.displayed_item_ids = [
                id for id in session.displayed_item_ids
                if id not in removed_ids
            ]
            timer.mark("DB Remove")

        elif intent == "ADD":
            new_search = intent_result.get("new_search", True)
            session.add_utterance(transcript, "ADD", new_search=new_search)
            # Exclude basket items so they don't reappear in search results
            exclude_ids = list(set(session.displayed_item_ids + session.basket_item_ids))
            if new_search:
                # Fresh search — only exclude basket items
                exclude_ids = session.basket_item_ids

            query_embedding = create_query_embedding(session.accumulated_criteria)
            timer.mark("Embedding")

            items = await search_menu_items(db, query_embedding, exclude_ids)
            timer.mark("DB Search")

            session.displayed_item_ids = [item.id for item in items]

        elif intent == "SELECT":
            select_names = intent_result.get("select_items", [])
            selected_ids = await get_item_ids_by_names_from_set(
                db, select_names, session.displayed_item_ids
            )
            if selected_ids:
                session.add_to_basket(selected_ids)
                session.displayed_item_ids = [
                    id for id in session.displayed_item_ids
                    if id not in selected_ids
                ]
                msg = f"Added {len(selected_ids)} item(s) to your order"
            else:
                msg = "Could not find those items in the current results"
            timer.mark("DB Select")

        elif intent == "REMOVE_FROM_BASKET":
            basket_remove_names = intent_result.get("basket_remove_items", [])
            removed_ids = await get_item_ids_by_names(db, basket_remove_names)
            session.remove_from_basket(removed_ids)
            msg = "Removed item(s) from your order"
            timer.mark("DB Basket Remove")

        elif intent == "CONFIRM":
            msg = "Order confirmed! Thank you!"

        # Fetch current search results and basket
        items = await get_items_by_ids(db, session.displayed_item_ids)
        basket_items_db = await get_items_by_ids(db, session.basket_item_ids)
        timer.mark("DB Fetch")

        timer.log()

        return AudioResponse(
            items=[menu_item_to_response(item) for item in items],
            basket_items=[menu_item_to_response(i) for i in basket_items_db],
            transcript=transcript,
            session_id=session.session_id,
            message=msg,
        )

    @post("/basket/add")
    async def add_to_basket(
        self,
        data: BasketActionRequest,
        db: AsyncSession,
    ) -> BasketActionResponse:
        """Add an item to basket via click."""
        session = get_or_create_session(data.session_id)
        session.add_to_basket([data.item_id])
        session.displayed_item_ids = [
            id for id in session.displayed_item_ids
            if id != data.item_id
        ]
        basket_items_db = await get_items_by_ids(db, session.basket_item_ids)
        return BasketActionResponse(
            basket_items=[menu_item_to_response(i) for i in basket_items_db],
            session_id=session.session_id,
            message="Item added to order",
        )

    @post("/basket/remove")
    async def remove_from_basket(
        self,
        data: BasketActionRequest,
        db: AsyncSession,
    ) -> BasketActionResponse:
        """Remove an item from basket via click."""
        session = get_or_create_session(data.session_id)
        session.remove_from_basket([data.item_id])
        basket_items_db = await get_items_by_ids(db, session.basket_item_ids)
        return BasketActionResponse(
            basket_items=[menu_item_to_response(i) for i in basket_items_db],
            session_id=session.session_id,
            message="Item removed from order",
        )
