# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Context:** FastAPI Service

## OVERVIEW
The core API service powered by FastAPI, handling data persistence, business logic, and search functionality. It exposes a RESTful API consumed by the frontend and other clients.

## FOLDER STRUCTURE
- `app/api/`: Route handlers and endpoints.
- `app/core/`: Configuration and lifespan management.
- `app/models/`: SQLModel database schemas.
- `app/services/`: Business logic layer (Service Pattern).
- `app/db/`: Database connection and session management.

## CORE BEHAVIORS & PATTERNS
- **Async First**: All I/O operations (DB, HTTP) must be `async/await`.
- **Service Layer**: Logic resides in `app/services/`, not in API routes.
- **Dependency Injection**: Use FastAPI's `Depends` for all resource access (DB sessions, services).
- **Pydantic V2**: Use strict typing and validation for all data schemas.

## CONVENTIONS
- **Testing**: `pytest` for unit/integration tests; mock external services.
- **Linting**: Strict `ruff` compliance; no unused imports.
- **Type Safety**: `mypy`/`ty` enabled; fully type-hinted codebases required.
- **Error Handling**: Use custom exceptions in `services/`, caught by global handlers.

## WORKING AGREEMENTS
- **No Global State**: Avoid global variables; use Dependency Injection.
- **Database Migrations**: Review `alembic` migrations before applying.
- **API Versioning**: Prefix all routes with `/api/v1`.
- **Documentation**: Keep docstrings up-to-date for OpenAPI generation.
