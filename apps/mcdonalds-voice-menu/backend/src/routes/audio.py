import base64
from litestar import Controller, post
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas import AudioRequest, AudioResponse, menu_item_to_response
from src.session import get_or_create_session
from src.services.azure_speech import transcribe_audio
from src.services.azure_openai import parse_intent
from src.services.retrieval import search_menu_items, get_items_by_ids, get_item_ids_by_names


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
        4. Return menu items
        """
        session = get_or_create_session(data.session_id)

        # Transcribe audio
        audio_bytes = base64.b64decode(data.audio_base64)
        transcript = await transcribe_audio(audio_bytes, session.language)

        if not transcript:
            return AudioResponse(
                transcript="",
                message="No speech was recognized in the recording",
            )

        # Parse intent
        intent_result = await parse_intent(transcript, session.conversation_history)

        # Handle intent
        if intent_result.get("intent") == "CLEAR":
            session.clear()
            return AudioResponse(
                transcript=transcript,
                message="Selection cleared",
            )

        elif intent_result.get("intent") == "REMOVE":
            remove_names = intent_result.get("remove_items", [])
            removed_ids = await get_item_ids_by_names(db, remove_names)
            session.displayed_item_ids = [
                id for id in session.displayed_item_ids
                if id not in removed_ids
            ]

        elif intent_result.get("intent") == "ADD":
            session.add_utterance(transcript, "ADD")
            items = await search_menu_items(db, session.accumulated_criteria, session.displayed_item_ids)
            session.displayed_item_ids = [item.id for item in items]

        # Fetch current items and convert to response structs
        items = await get_items_by_ids(db, session.displayed_item_ids)

        return AudioResponse(
            items=[menu_item_to_response(item) for item in items],
            transcript=transcript,
            session_id=session.session_id,
        )