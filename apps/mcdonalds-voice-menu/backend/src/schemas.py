from msgspec import Struct

from src.models import MenuItem


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
    basket_items: list[MenuItemResponse] = []
    transcript: str = ""
    session_id: str = ""
    message: str = ""


class BasketActionRequest(Struct):
    """Request body for click-based basket add/remove."""
    session_id: str
    item_id: int


class BasketActionResponse(Struct):
    """Response body for basket actions."""
    basket_items: list[MenuItemResponse] = []
    session_id: str = ""
    message: str = ""


def menu_item_to_response(item: MenuItem) -> MenuItemResponse:
    """Convert a SQLAlchemy MenuItem to a MenuItemResponse struct."""
    return MenuItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        tags=item.tags,
        image_url=item.image_url,
        name_de=item.name_de,
        name_cs=item.name_cs,
        description_de=item.description_de,
        description_cs=item.description_cs
    )