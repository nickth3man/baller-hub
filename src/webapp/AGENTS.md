# src/webapp AGENTS.md

**Context:** Full-stack webapp (FastAPI backend + Next.js frontend). (src/webapp/backend/pyproject.toml:13, src/webapp/frontend/package.json:13)
**Override Justification:** Backend and frontend have separate manifests and dev commands. (src/webapp/backend/pyproject.toml:1, src/webapp/frontend/package.json:1, src/webapp/README.md:74)

See root `../../AGENTS.md` for project-wide conventions.

## Overview
Backend serves `/api/v1` endpoints and frontend uses the Next.js App Router. (src/webapp/backend/app/main.py:36, src/webapp/README.md:48)

## Commands (Overrides)

```bash
# Backend dev server (src/webapp/README.md:74, src/webapp/README.md:76)
cd src/webapp/backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend dev server (src/webapp/README.md:81, src/webapp/README.md:83)
cd src/webapp/frontend
npm install
npm run dev

# Full stack with Docker (src/webapp/README.md:58, src/webapp/README.md:59)
cd src/webapp
docker compose up -d

# Seed data + index (src/webapp/README.md:92, src/webapp/README.md:93)
cd src/webapp
python -m scripts.seed_db --bootstrap
```

## Conventions (Overrides)
- Backend uses absolute imports from `app`. (src/webapp/backend/app/main.py:8)
- API routes are mounted under `/api/v1`. (src/webapp/backend/app/main.py:36)
- Frontend uses `@/*` path aliasing. (src/webapp/frontend/tsconfig.json:21)
- Frontend rewrites proxy API calls to the backend base URL. (src/webapp/frontend/next.config.js:19)

## Files Never to Modify
> TODO: Webapp-specific protected files are not documented.

## Unknowns & TODOs
> TODO: Confirm whether migrations or lock files have explicit immutability rules.
