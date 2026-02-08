from litestar import Controller, get
from litestar.di import Provide
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dto import MenuItemReadDTO
from src.models import MenuItem


class MenuController(Controller):
    path = "/api/menu"
    dependencies = {"db": Provide(get_db_session)}
    return_dto = MenuItemReadDTO

    @get("/")
    async def get_menu_items(self, db: AsyncSession) -> list[MenuItem]:
        """Get all menu items from the database."""
        result = await db.execute(select(MenuItem))
        return list(result.scalars().all())

    @get("/categories", return_dto=None)
    async def get_categories(self, db: AsyncSession) -> list[str]:
        """Get all unique categories from the database."""
        result = await db.execute(select(distinct(MenuItem.category)))
        return list(result.scalars().all())

    @get("/category/{category: str}")
    async def get_by_category(
        self,
        category: str,
        db: AsyncSession,
    ) -> list[MenuItem]:
        """Get all menu items by category."""
        result = await db.execute(select(MenuItem).where(MenuItem.category == category))
        return list(result.scalars().all())

    