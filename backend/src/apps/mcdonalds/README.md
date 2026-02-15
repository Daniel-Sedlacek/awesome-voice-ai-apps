# McDonald's Voice Menu Ordering

Voice-controlled fast-food ordering system. Users browse a menu, search for items with natural language, and build a shopping basket — all through voice commands.

## How It Works

1. **Streaming STT** — Audio is captured via WebSocket and transcribed in real time (Azure Speech or Deepgram).
2. **Intent Parsing** — Azure OpenAI classifies the transcript into an intent: `ADD`, `REMOVE`, `SELECT`, `REMOVE_FROM_BASKET`, `CLEAR`, or `CONFIRM`.
3. **Semantic Search** — For `ADD` intents, the query is embedded with sentence-transformers, matched against menu items via pgvector cosine similarity, and reranked with a cross-encoder.
4. **Session Management** — An in-memory session tracks language, conversation history, displayed items, and basket contents with quantities.

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| WS | `/ws/mcdonalds/audio` | Streaming STT + full pipeline |
| POST | `/api/mcdonalds/basket/add` | Add item to basket (click) |
| POST | `/api/mcdonalds/basket/remove` | Remove item from basket (click) |
| GET | `/api/mcdonalds/menu/` | All menu items |
| GET | `/api/mcdonalds/menu/categories` | Distinct categories |
| GET | `/api/mcdonalds/menu/category/{category}` | Items by category |

## Quickstart

This app requires PostgreSQL with the pgvector extension.

```bash
# 1. Start the database
docker compose up db

# 2. Install dependencies
cd backend
uv sync

# 3. Run migrations
uv run alembic upgrade head

# 4. Seed the menu (creates embeddings and inserts items)
uv run python -m scripts.seed_database

# 5. Start the backend
uv run litestar run --reload --host 0.0.0.0 --port 8000
```

## Required Environment Variables

```
DATABASE_URL=postgresql+asyncpg://mcdonalds:mcdonalds@localhost:5432/mcdonalds_menu
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=westeurope
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
```
