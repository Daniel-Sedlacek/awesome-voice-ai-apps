from __future__ import annotations

import abc
from collections.abc import Callable, Awaitable


class StreamingSTTSession(abc.ABC):
    """Base class for streaming speech-to-text sessions.

    Providers implement start/send_audio/stop to pipe live PCM audio
    into a continuous recogniser and fire callbacks on interim/final results.
    """

    @abc.abstractmethod
    async def start(
        self,
        language: str,
        on_interim: Callable[[str], Awaitable[None]],
        on_final: Callable[[str], Awaitable[None]],
    ) -> None:
        """Begin continuous recognition for *language*.

        *on_interim* is called with partial transcripts as they arrive.
        *on_final* is called when the recogniser commits a sentence.
        """

    @abc.abstractmethod
    async def send_audio(self, chunk: bytes) -> None:
        """Feed a chunk of raw 16 kHz 16-bit mono PCM audio."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop recognition and release resources."""
