from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Text, ARRAY
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(100))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(100)))
    image_url: Mapped[str] = mapped_column(String(200))
    embedding: Mapped[list[float]] = mapped_column(Vector(1024))

    # Multilingual fields (for display only, embeddings are in English)
    name_de: Mapped[str] = mapped_column(String(200), nullable=True)
    name_cs: Mapped[str] = mapped_column(String(200), nullable=True)
    description_de: Mapped[str] = mapped_column(Text, nullable=True)
    description_cs: Mapped[str] = mapped_column(Text, nullable=True)