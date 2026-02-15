import time

from litestar import Controller, post
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas import (
    AudioResponse,
    BasketActionRequest,
    BasketActionResponse,
    menu_item_to_response,
)
from src.session import UserSession, get_or_create_session
from src.services.azure_openai import parse_intent
from src.services.embeddings import create_query_embedding
from src.services.retrieval import (
    search_menu_items,
    get_items_by_ids,
    get_item_ids_by_names,
    get_item_ids_by_names_from_set,
    get_item_names_by_ids,
)
from src.services.reranker import rerank_items
from src.settings import get_settings

settings = get_settings()

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
        print(f"  Pipeline Timing: {settings.STT_PROVIDER} as a STT provider")
        print(f"  {parts}")
        print(f"  Total: {total * 1000:.0f}ms")
        print(f"{'=' * 60}\n")


def _basket_responses(items_db, session: UserSession):
    """Build basket item responses preserving session order and including quantities."""
    by_id = {item.id: item for item in items_db}
    return [
        menu_item_to_response(by_id[item_id], session.basket_quantities.get(item_id, 1))
        for item_id in session.basket_item_ids
        if item_id in by_id
    ]


async def _map_names_to_ids(
    db: AsyncSession, names, candidate_ids: list[int]
) -> dict[str, int]:
    """Map item names (from LLM) to their IDs, case-insensitive."""
    from sqlalchemy import select, func
    from src.models import MenuItem

    if not names or not candidate_ids:
        return {}
    name_list = list(names)
    query = select(MenuItem.id, MenuItem.name).where(
        func.lower(MenuItem.name).in_([n.lower() for n in name_list]),
        MenuItem.id.in_(candidate_ids),
    )
    result = await db.execute(query)
    # Build a lowercase DB name → id map, then match against LLM names
    db_lower_map = {row.name.lower(): row.id for row in result.all()}
    return {name: db_lower_map[name.lower()] for name in name_list if name.lower() in db_lower_map}


async def run_pipeline(
    session: UserSession,
    transcript: str,
    db: AsyncSession,
    timer: PipelineTimer | None = None,
) -> AudioResponse:
    """Run the intent-parse → search/modify → response pipeline.

    Shared by the REST endpoint and the WebSocket handler.
    """
    if timer is None:
        timer = PipelineTimer()

    if not transcript:
        basket_items_db = await get_items_by_ids(db, session.basket_item_ids)
        timer.log()
        return AudioResponse(
            transcript="",
            message="No speech was recognized in the recording",
            session_id=session.session_id,
            basket_items=_basket_responses(basket_items_db, session),
        )

    # Fetch current item names for LLM context
    displayed_names = await get_item_names_by_ids(db, session.displayed_item_ids)
    basket_names = await get_item_names_by_ids(db, session.basket_item_ids)

    # Parse intent
    intent_result = await parse_intent(
        transcript, session.conversation_history, displayed_names, basket_names
    )
    intent = intent_result.get("intent")
    timer.mark("LLM")
    msg = ""

    if intent == "CLEAR":
        session.clear()
        timer.log()
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
        search_criteria = intent_result.get("search_criteria")
        session.add_utterance(transcript, "ADD", new_search=new_search, search_criteria=search_criteria)
        exclude_ids = list(set(session.displayed_item_ids + session.basket_item_ids))
        if new_search:
            exclude_ids = session.basket_item_ids

        query_embedding = create_query_embedding(session.accumulated_criteria)
        timer.mark("Embedding")

        items = await search_menu_items(db, query_embedding, exclude_ids)
        timer.mark("DB Search")

        items = rerank_items(session.accumulated_criteria, items)
        timer.mark("Rerank")

        session.displayed_item_ids = [item.id for item in items]

    elif intent == "SELECT":
        select_names = intent_result.get("select_items", [])
        select_quantities_by_name = intent_result.get("select_quantities", {})
        selected_ids = await get_item_ids_by_names_from_set(
            db, select_names, session.displayed_item_ids
        )
        if selected_ids:
            # Map name-based quantities to ID-based quantities
            quantities_by_id: dict[int, int] = {}
            if select_quantities_by_name:
                name_to_id = await _map_names_to_ids(db, select_quantities_by_name.keys(), selected_ids)
                for name, qty in select_quantities_by_name.items():
                    item_id = name_to_id.get(name)
                    if item_id:
                        quantities_by_id[item_id] = qty
            session.add_to_basket(selected_ids, quantities_by_id or None)
            session.displayed_item_ids = [
                id for id in session.displayed_item_ids
                if id not in selected_ids
            ]
            total_qty = sum(quantities_by_id.get(id, 1) for id in selected_ids)
            msg = f"Added {total_qty} item(s) to your order"
            timer.mark("DB Select")
        else:
            search_text = " ".join(select_names)
            session.add_utterance(transcript, "ADD", new_search=True, search_criteria=search_text)
            exclude_ids = session.basket_item_ids

            query_embedding = create_query_embedding(session.accumulated_criteria)
            timer.mark("Embedding")

            items = await search_menu_items(db, query_embedding, exclude_ids)
            timer.mark("DB Search")

            items = rerank_items(session.accumulated_criteria, items)
            timer.mark("Rerank")

            session.displayed_item_ids = [item.id for item in items]

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
        basket_items=_basket_responses(basket_items_db, session),
        transcript=transcript,
        session_id=session.session_id,
        message=msg,
    )


class AudioController(Controller):
    path = "/api"
    dependencies = {"db": Provide(get_db_session)}

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
            basket_items=_basket_responses(basket_items_db, session),
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
            basket_items=_basket_responses(basket_items_db, session),
            session_id=session.session_id,
            message="Item removed from order",
        )
