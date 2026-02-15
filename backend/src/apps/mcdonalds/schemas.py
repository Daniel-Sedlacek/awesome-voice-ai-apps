from typing import Annotated

from msgspec import Meta, Struct

from src.models import MenuItem


class MenuItemResponse(Struct):
    """Serializable menu item for the audio endpoint response (excluding embedding)."""
    id: Annotated[int, Meta(ge=1, description="Menu item database ID")]
    name: Annotated[str, Meta(description="Item name in English")]
    description: Annotated[str, Meta(description="Item description in English")]
    price: Annotated[float, Meta(ge=0, description="Item price in EUR")]
    category: Annotated[str, Meta(description="Menu category")]
    tags: Annotated[list[str], Meta(description="Searchable tags")]
    image_url: Annotated[str, Meta(description="Path to item image")]
    name_de: Annotated[str | None, Meta(description="Item name in German")] = None
    name_cs: Annotated[str | None, Meta(description="Item name in Czech")] = None
    description_de: Annotated[str | None, Meta(description="Item description in German")] = None
    description_cs: Annotated[str | None, Meta(description="Item description in Czech")] = None
    quantity: Annotated[int, Meta(ge=1, description="Quantity in basket")] = 1


class AudioResponse(Struct):
    """Response body for the audio processing endpoint."""
    items: Annotated[list[MenuItemResponse], Meta(description="Matched menu items")] = []
    basket_items: Annotated[list[MenuItemResponse], Meta(description="Current basket contents")] = []
    transcript: Annotated[str, Meta(description="Speech-to-text transcription")] = ""
    session_id: Annotated[str, Meta(description="Conversation session identifier")] = ""
    message: Annotated[str, Meta(description="Assistant message to display")] = ""
    confirmed: Annotated[bool, Meta(description="Whether the order was confirmed")] = False


class BasketActionRequest(Struct):
    """Request body for click-based basket add/remove."""
    session_id: Annotated[str, Meta(description="Conversation session identifier")]
    item_id: Annotated[int, Meta(ge=1, description="Menu item ID to add or remove")]


class BasketActionResponse(Struct):
    """Response body for basket actions."""
    basket_items: Annotated[list[MenuItemResponse], Meta(description="Updated basket contents")] = []
    session_id: Annotated[str, Meta(description="Conversation session identifier")] = ""
    message: Annotated[str, Meta(description="Action result message")] = ""


def menu_item_to_response(item: MenuItem, quantity: int = 1) -> MenuItemResponse:
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
        description_cs=item.description_cs,
        quantity=quantity,
    )
