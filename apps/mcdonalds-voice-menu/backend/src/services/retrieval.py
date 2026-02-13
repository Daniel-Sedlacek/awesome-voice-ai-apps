from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import MenuItem
from src.services.embeddings import create_query_embedding


async def search_menu_items(
    session: AsyncSession, query: str, exclude_ids: list[int] | None = None, top_k: int = 5
) -> list[MenuItem]:
    """Search menu items based on query using vector similarity search."""
    # Create query embedding with instructions prefix
    query_embedding = create_query_embedding(query)

    # Search by cosine similarity
    select_query = (
        select(MenuItem)
        .order_by(MenuItem.embedding.cosine_distance(query_embedding))
    )
    if exclude_ids:
        select_query = select_query.where(MenuItem.id.notin_(exclude_ids))
    select_query = select_query.limit(top_k)
    result = await session.execute(select_query)
    return result.scalars().all()


async def get_items_by_ids(
    session: AsyncSession, item_ids: list[int]
) -> list[MenuItem]:
    """Get menu items by their IDs."""
    if not item_ids:
        return []

    select_query = select(MenuItem).where(MenuItem.id.in_(item_ids))
    result = await session.execute(select_query)
    return result.scalars().all()


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
