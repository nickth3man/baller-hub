# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Context:** Full Stack Orchestration

## OVERVIEW
This directory orchestrates the full stack application, connecting the FastAPI backend, Next.js frontend, and database services. It serves as the integration point for running the complete Baller Hub platform locally.

## FOLDER STRUCTURE
- `backend/`: FastAPI service source code.
- `frontend/`: Next.js application source code.
- `scripts/`: Utility scripts for orchestration and maintenance.
- `baller.duckdb`: Local database file (git-ignored).

## CORE BEHAVIORS & PATTERNS
- **Port Allocation**:
    - Backend: `8000` (API Docs: `/docs`).
    - Frontend: `3000`.
    - Database: Standard DuckDB file access.
- **Integration**: Backend and Frontend communicate via local network or mapped ports.

## CONVENTIONS
- **Environment**: `.env` files manage configuration secrets.
- **Scripts**: Run orchestration tasks via `scripts/` (e.g., `dev.sh`, `up.sh`).

## WORKING AGREEMENTS
- **Configuration**: Do not commit secrets/credentials to git.
- **Ports**: Verify port availability before starting services.
- **Shutdown**: Ensure processes are terminated after development.

