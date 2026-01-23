# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Context:** Full Stack Orchestration

## OVERVIEW
This directory orchestrates the full stack application, connecting the FastAPI backend, Next.js frontend, and database services via Docker. It serves as the integration point for running the complete Baller Hub platform locally.

## FOLDER STRUCTURE
- `backend/`: FastAPI service source code.
- `frontend/`: Next.js application source code.
- `docker/`: Container configurations and Compose files.
- `scripts/`: Utility scripts for orchestration and maintenance.
- `baller.duckdb`: Local database file (git-ignored).

## CORE BEHAVIORS & PATTERNS
- **Containerization**: All services defined in `docker-compose.yml`.
- **Port Allocation**:
    - Backend: `8000` (API Docs: `/docs`).
    - Frontend: `3000`.
    - Database: Standard DuckDB file access.
- **Integration**: Backend and Frontend communicate via internal Docker network or mapped ports locally.

## CONVENTIONS
- **Docker**: Use `docker-compose` for orchestration.
- **Environment**: `.env` files manage configuration secrets.
- **Scripts**: Run orchestration tasks via `scripts/` (e.g., `dev.sh`, `up.sh`).
- **Logs**: Monitor service logs via `docker-compose logs -f`.

## WORKING AGREEMENTS
- **Configuration**: Do not commit secrets/credentials to git.
- **Ports**: Verify port availability before starting services.
- **Dependencies**: Rebuild containers when adding system-level dependencies.
- **Shutdown**: Use `docker-compose down` to clean up resources.
