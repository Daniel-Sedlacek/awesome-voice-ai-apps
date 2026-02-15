import base64
import logging
from dataclasses import dataclass

import msgspec
from litestar import WebSocket
from litestar.handlers import WebsocketListener

from src.database import async_session
from src.apps.mcdonalds.routes.audio import PipelineTimer, run_pipeline
from src.apps.mcdonalds.services.phrase_hints import get_menu_phrases
from src.shared.stt import create_streaming_session
from src.shared.stt.streaming import StreamingSTTSession
from src.apps.mcdonalds.session import UserSession, get_or_create_session

logger = logging.getLogger(__name__)


@dataclass
class ConnectionState:
    session: UserSession | None = None
    stt_session: StreamingSTTSession | None = None


class AudioWSListener(WebsocketListener):
    path = "/ws/mcdonalds/audio"
    receive_mode = "text"
    send_mode = "text"

    _connections: dict[int, ConnectionState] = {}

    async def on_accept(self, socket: WebSocket) -> None:
        self._connections[id(socket)] = ConnectionState()

    async def on_receive(self, data: str, socket: WebSocket) -> None:
        try:
            msg = msgspec.json.decode(data.encode() if isinstance(data, str) else data)
        except Exception:
            return

        if not isinstance(msg, dict):
            return

        msg_type = msg.get("type")
        conn = self._connections.get(id(socket))
        if conn is None:
            return

        if msg_type == "start":
            await self._handle_start(msg, conn, socket)
        elif msg_type == "audio":
            await self._handle_audio(msg, conn)
        elif msg_type == "stop":
            await self._handle_stop(conn)

    async def on_disconnect(self, socket: WebSocket) -> None:
        conn = self._connections.pop(id(socket), None)
        if conn and conn.stt_session:
            await conn.stt_session.stop()

    async def _handle_start(
        self, msg: dict, conn: ConnectionState, socket: WebSocket
    ) -> None:
        session_id = msg.get("session_id")
        language = msg.get("language", "en-US")

        conn.session = get_or_create_session(session_id)
        conn.session.language = language

        stt_session = create_streaming_session()
        conn.stt_session = stt_session

        async def on_interim(text: str) -> None:
            try:
                await socket.send_json({"type": "interim", "text": text})
            except Exception:
                pass

        async def on_final(text: str) -> None:
            try:
                await socket.send_json({"type": "processing", "text": text})
                timer = PipelineTimer()
                async with async_session() as db:
                    response = await run_pipeline(conn.session, text, db, timer)
                result = msgspec.to_builtins(response)
                result["type"] = "results"
                await socket.send_json(result)
                await socket.send_json({"type": "ready"})
            except Exception:
                logger.exception("Pipeline error in WS on_final")
                try:
                    await socket.send_json(
                        {"type": "error", "message": "Pipeline processing failed"}
                    )
                    await socket.send_json({"type": "ready"})
                except Exception:
                    pass

        phrases = get_menu_phrases(language)
        await stt_session.start(language, on_interim, on_final, phrase_hints=phrases)
        await socket.send_json({
            "type": "connected",
            "session_id": conn.session.session_id,
        })

    async def _handle_audio(self, msg: dict, conn: ConnectionState) -> None:
        if not conn.stt_session:
            return
        audio_b64 = msg.get("data")
        if not audio_b64:
            return
        pcm_bytes = base64.b64decode(audio_b64)
        await conn.stt_session.send_audio(pcm_bytes)

    async def _handle_stop(self, conn: ConnectionState) -> None:
        if conn.stt_session:
            await conn.stt_session.stop()
            conn.stt_session = None
