# src/webapp/backend AGENTS.md

**Generated:** 2026-01-22
**Context:** FastAPI backend service.

## OVERVIEW
The REST API server for Baller Hub, built with FastAPI. It handles data persistence (PostgreSQL), search (Meilisearch), and serves the frontend.

## FOLDER STRUCTURE
- `app/api/v1/`: Versioned API route handlers.
- `app/core/`: Configuration and environment settings.
- `app/db/`: Database session management and migrations.
- `app/models/`: SQLModel (SQLAlchemy + Pydantic) database tables.
- `app/services/`: Business logic layer isolated from HTTP transport.
- `tests/`: Backend-specific test suite.

## CORE BEHAVIORS & PATTERNS
- **Service Layer**: Business logic resides in `services/`, not in route handlers.
- **Async Database**: All database interactions use asynchronous sessions.
- **Dependency Injection**: FastAPI `Depends` is used for service and database access.

## CONVENTIONS
- **Commands**: `uv run uvicorn` (run), `uv run alembic` (db), `uv run ruff check` (lint), `uv run ty check` (type).
- **Naming**: Snake_case for models and schemas.
- **Imports**: Absolute imports from `app` (e.g., `from app.core import config`).

## WORKING AGREEMENTS
- **Secrets**: Never commit secrets. Use `.env` file and `app/core/config.py`.
- **Migrations**: Always generate a migration when modifying `models/`.
- **No Sync I/O**: Avoid blocking calls in async route handlers.
