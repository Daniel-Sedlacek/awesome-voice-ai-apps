import asyncio
import json
from pathlib import Path
from sqlalchemy import text

from src.database import async_session
from src.models import MenuItem
from src.services.embeddings import create_batch_document_embeddings


async def seed_database():
    """Load menu items, create embeddings, and insert into database."""

    print("Loading menu items from JSON file...")

    # Load menu items from JSON file
    data_path = Path(__file__).parent.parent / "data" / "menu_items.json"
    with open(data_path, encoding="utf-8") as f:
        items = json.load(f)

    print(f"Creating embeddings for {len(items)} menu items...")

    # Create embeddings for all items (batch for efficiency)
    text_for_embeddings = [f"{item['name']}: {item['description']}" for item in items]
    embeddings = create_batch_document_embeddings(text_for_embeddings)

    async with async_session() as session:
        # Clear existing items
        await session.execute(
            text("TRUNCATE  TABLE menu_items RESTART IDENTITY CASCADE")
        )

        for item_data, embedding in zip(items, embeddings):
            item = MenuItem(
                name=item_data["name"],
                name_de=item_data["name_de"],
                name_cs=item_data["name_cs"],
                description=item_data["description"],
                description_de=item_data["description_de"],
                description_cs=item_data["description_cs"],
                price=item_data["price"],
                category=item_data["category"],
                tags=item_data["tags"],
                image_url=item_data["image_url"],
                embedding=embedding,
            )
            session.add(item)

        await session.commit()
        print(f"✅ Seeded {len(items)} menu items with embeddings")


if __name__ == "__main__":
    asyncio.run(seed_database())