# src/webapp AGENTS.md

**Context:** Orchestration for Full Stack (FastAPI + Next.js).
**Children:** `backend/AGENTS.md`, `frontend/AGENTS.md`

## OVERVIEW
Monorepo-style structure within `src/webapp`.
- **Backend:** Python/FastAPI (`backend/`)
- **Frontend:** TypeScript/Next.js (`frontend/`)

## COMMANDS
```bash
# Full Stack (Docker)
docker compose up -d

# Seed Data
python -m scripts.seed_db --bootstrap
```

## ARCHITECTURE
- **Frontend** proxies `/api/v1` -> **Backend**.
- **Backend** talks to **Postgres** (Data), **Redis** (Cache), **Meilisearch** (Search).
- **Ingestion** scripts run in Backend context but import from `src/scraper`.

## WHERE TO LOOK
- **API Logic:** `backend/AGENTS.md`
- **UI/Components:** `frontend/AGENTS.md`
- **Data Models:** `backend/app/models`
