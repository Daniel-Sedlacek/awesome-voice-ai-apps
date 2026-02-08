from msgspec import Struct


class AudioRequest(Struct):
    """Request body for the audio processing endpoint."""
    audio_base64: str
    session_id: str | None = None
    language: str = "en-US"


class MenuItemResponse(Struct):
    """Serializable menu item for the audio endpoint response (excluding embedding)."""
    id: int
    name: str
    description: str
    price: float
    category: str
    tags: list[str]
    image_url: str
    name_de: str | None = None
    name_cs: str | None = None
    description_de: str | None = None
    description_cs: str | None = None


class AudioResponse(Struct):
    """Response body for the audio processing endpoint."""
    items: list[MenuItemResponse] = []
    transcript: str = ""
    session_id: str = ""
    message: str = ""