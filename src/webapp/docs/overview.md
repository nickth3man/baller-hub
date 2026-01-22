# Webapp Overview

Baller Hub is a full-stack web application that serves scraped basketball data
through a FastAPI backend and a Next.js App Router frontend. The backend stores
data in PostgreSQL and exposes REST endpoints under `/api/v1`.

## High-Level Flow

1. Data enters the system via CSV ingestion or scraper-based seeding.
2. Ingestion writes normalized data into PostgreSQL.
3. FastAPI services query SQLModel models and return JSON responses.
4. Next.js server components fetch from the API and render pages.

## Key Directories

- `src/webapp/backend/app` - FastAPI app, models, services, ingestion
- `src/webapp/frontend/app` - Next.js App Router pages
- `src/webapp/frontend/(components)` - Shared UI components
- `src/webapp/scripts` - Database seeding and indexing scripts
- `src/webapp/docs` - Webapp documentation

## Local Setup

Backend:

```bash
cd src/webapp/backend
uv sync
uv run uvicorn app.main:app --reload
```

Frontend:

```bash
cd src/webapp/frontend
npm install
npm run dev
```

## Environment Variables

Backend expects:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your_key
SECRET_KEY=your_secret
```

See `src/webapp/backend/.env.example` for the full template.
