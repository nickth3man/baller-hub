# src/webapp/backend AGENTS.md

**Context:** FastAPI backend for Baller Hub.
**Parent:** `../AGENTS.md` (Webapp), `../../AGENTS.md` (Root)

## STRUCTURE
```
backend/
├── app/
│   ├── api/v1/      # Routers
│   ├── core/        # Config (env vars)
│   ├── db/          # SQLModel session
│   ├── models/      # Database models
│   ├── schemas/     # Pydantic DTOs
│   ├── services/    # Business logic
│   └── ingestion/   # Scraper integration
├── tests/           # Backend-specific tests
└── alembic/         # DB migrations
```

## COMMANDS
```bash
# Dev Server
uv run uvicorn app.main:app --reload

# Database
uv run alembic upgrade head    # Migrate
python -m scripts.seed_db      # Seed

# Tests
uv run pytest tests/
```

## CONVENTIONS
- **Imports:** Absolute from `app` (e.g., `from app.models import Player`).
- **DB Models:** SQLModel with snake_case table names.
- **API:** Versioned routers (`/api/v1`).
- **Async:** All DB operations must be async.

## ANTI-PATTERNS
- Sync DB calls in async routes.
- Hardcoded secrets (use `.env`).
- Circular imports in models (use string forward refs).
