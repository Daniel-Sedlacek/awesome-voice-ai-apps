from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from litestar.dto import DTOConfig

from src.models import MenuItem


class MenuItemReadDTO(SQLAlchemyDTO[MenuItem]):
    config = DTOConfig(exclude=["embedding"])