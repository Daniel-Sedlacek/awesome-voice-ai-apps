import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import MenuItem

logger = logging.getLogger(__name__)

MAX_RESULTS = 20
COSINE_DISTANCE_THRESHOLD = 0.8


async def search_menu_items(
    session: AsyncSession,
    query_embedding: list[float],
    exclude_ids: list[int] | None = None,
) -> list[MenuItem]:
    """Search menu items by embedding similarity, filtered by cosine distance threshold."""
    distance = MenuItem.embedding.cosine_distance(query_embedding)
    select_query = (
        select(MenuItem, distance.label("cosine_distance"))
        .where(distance <= COSINE_DISTANCE_THRESHOLD)
        .order_by(distance)
    )
    if exclude_ids:
        select_query = select_query.where(MenuItem.id.notin_(exclude_ids))
    select_query = select_query.limit(MAX_RESULTS)
    result = await session.execute(select_query)
    rows = result.all()
    items = []
    for item, cosine_dist in rows:
        similarity = 1 - cosine_dist
        logger.info("Menu match: '%s' (similarity: %.4f)", item.name, similarity)
        items.append(item)
    return items


async def get_items_by_ids(
    session: AsyncSession, item_ids: list[int]
) -> list[MenuItem]:
    """Get menu items by their IDs."""
    if not item_ids:
        return []

    select_query = select(MenuItem).where(MenuItem.id.in_(item_ids))
    result = await session.execute(select_query)
    return result.scalars().all()


async def get_item_names_by_ids(
    session: AsyncSession, item_ids: list[int]
) -> list[str]:
    """Get menu item names by their IDs (lightweight, no embedding data)."""
    if not item_ids:
        return []

    select_query = select(MenuItem.name).where(MenuItem.id.in_(item_ids))
    result = await session.execute(select_query)
    return list(result.scalars().all())


async def get_item_ids_by_names_from_set(
    session: AsyncSession, names: list[str], candidate_ids: list[int]
) -> list[int]:
    """Get menu item IDs by name (case-insensitive), restricted to a candidate set of IDs."""
    if not names or not candidate_ids:
        return []

    select_query = select(MenuItem.id).where(
        func.lower(MenuItem.name).in_([str(n).lower() for n in names]),
        MenuItem.id.in_(candidate_ids),
    )
    result = await session.execute(select_query)
    return list(result.scalars().all())


async def get_item_ids_by_names(session: AsyncSession, names: list[str]) -> list[int]:
    """Get menu item IDs by their names (case-insensitive)."""
    if not names:
        return []

    select_query = select(MenuItem.id).where(
        func.lower(MenuItem.name).in_([str(n).lower() for n in names])
    )
    result = await session.execute(select_query)
    return list(result.scalars().all())
