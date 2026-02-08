from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import MenuItem
from src.services.embeddings import create_query_embedding


async def search_menu_items(
    session: AsyncSession, query: str, top_k: int = 5
) -> list[MenuItem]:
    """Search menu items based on query using vector similarity search."""
    # Create query embedding with instructions prefix
    query_embedding = create_query_embedding(query)

    # Search by cosine similarity
    select_query = (
        select(MenuItem)
        .order_by(MenuItem.embedding.cosine_similarity(query_embedding))
        .limit(top_k)
    )
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


async def get_item_ids_by_names(session: AsyncSession, names: list[str]) -> list[int]:
    """Get menu item IDs by their names (case-insensitive)."""
    if not names:
        return []

    select_query = select(MenuItem.id).where(
        func.lower(MenuItem.name).in_([str(n).lower() for n in names])
    )
    result = await session.execute(select_query)
    return list(result.scalars().all())
