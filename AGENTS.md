# AGENTS.md

## Project Overview
Baller Hub is a basketball-reference.com clone that includes a Python scraper plus a FastAPI backend and Next.js frontend; the scraper depends on lxml and emits JSON/CSV outputs. (README.md:3, pyproject.toml:26, src/scraper/output/writers.py:135, src/scraper/output/writers.py:172, src/webapp/backend/pyproject.toml:13, src/webapp/frontend/package.json:13)

## Repository Structure
- **src/scraper/** - Scraper library (client facade, HTML wrappers, parsers, output). (src/scraper/api/client.py:1, src/scraper/html/box_scores.py:1, src/scraper/parsers/box_scores.py:1, src/scraper/output/service.py:1)
- **src/webapp/backend/** - FastAPI API entrypoint and routers. (src/webapp/backend/app/main.py:1, src/webapp/backend/app/api/v1/router.py:1)
- **src/webapp/frontend/** - Next.js App Router pages and components. (src/webapp/README.md:48, src/webapp/frontend/app/layout.tsx:1)
- **tests/** - Unit, integration, and end-to-end test suites. (tests/unit/test_http_service.py:1, tests/integration/parsers/test_parse_draft.py:1, tests/end to end/test_client.py:1)
- **docs/** - Scraper/fixture guidance and repo docs. (docs/scraping-guide.md:1)
- **raw-data/** - CSV datasets used by ingestion. (src/webapp/docs/data-ingestion.md:5)
- **.github/workflows/** - CI pipeline definitions. (.github/workflows/ci.yml:1)

## Tech Stack
- **Language(s):** Python >=3.12 (scraper/backend), TypeScript 5.7 (frontend). (pyproject.toml:19, src/webapp/backend/pyproject.toml:10, src/webapp/frontend/package.json:31)
- **Framework(s):** FastAPI 0.115, Next.js 15, SQLModel ORM. (src/webapp/backend/pyproject.toml:13, src/webapp/frontend/package.json:13, src/webapp/backend/pyproject.toml:17)
- **Package Manager:** uv, npm. (README.md:18, src/webapp/README.md:82)
- **Key Libraries:** lxml, requests, asyncpg, meilisearch, @tanstack/react-query. (pyproject.toml:26, pyproject.toml:28, src/webapp/backend/pyproject.toml:18, src/webapp/backend/pyproject.toml:26, src/webapp/frontend/package.json:16)

## Build & Development Commands

### File-Scoped Commands (Preferred for Fast Feedback)

```bash
# Type check single file (CLAUDE.md:36)
uv run ty check path/to/file.py

# Lint single file (CLAUDE.md:39)
uv run ruff check path/to/file.py

# Format single file (CLAUDE.md:42)
uv run ruff format path/to/file.py

# Test single file (CLAUDE.md:45)
uv run pytest tests/unit/path/to/test_file.py -v
```

### Project-Wide Commands (Use Sparingly)

```bash
# Install dependencies (CI: .github/workflows/ci.yml:29)
uv sync

# Full test suite (CI: .github/workflows/ci.yml:35)
uv run pytest

# Full lint (CI: .github/workflows/ci.yml:31)
uv run ruff check .

# Full type check (CI: .github/workflows/ci.yml:33)
uv run ty check .
```

## Code Style & Conventions

### Formatting
- **Indentation:** 4 spaces (Python), 2 spaces (TypeScript/TSX). (src/scraper/api/client.py:67, src/webapp/frontend/app/page.tsx:7)
- **Formatter:** ruff (Python) and prettier (frontend). (pyproject.toml:63, src/webapp/frontend/package.json:10)
- **Line Length:** 88 characters (Python). (pyproject.toml:64)

### Naming Conventions
- **Variables/Functions:** snake_case in Python (e.g., `player_box_scores`). (src/scraper/api/client.py:88)
- **Types/Classes:** PascalCase (e.g., `HTTPService`). (src/scraper/services/http.py:31)
- **Constants:** SCREAMING_SNAKE_CASE (e.g., `PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX`). (src/scraper/parsers/base.py:3)

### Import Organization
Python uses ruff-isort with first-party packages `src.scraper` and `app`, and code uses absolute imports from those roots. (pyproject.toml:85, src/webapp/backend/pyproject.toml:79, src/scraper/api/client.py:15, src/webapp/backend/app/main.py:8)

## Architecture Notes

### High-Level Overview

```text
[Next.js frontend] -> [FastAPI API] -> [PostgreSQL/Redis/Meilisearch]
           |
           v
[Scraper client -> HTTPService -> ParserService -> OutputService]
```

(Sources: src/webapp/README.md:41, src/webapp/README.md:42, src/webapp/README.md:43, src/scraper/api/client.py:5)

### Key Components
- **Entry Point(s):** Scraper facade `src/scraper/api/client.py`, backend app `src/webapp/backend/app/main.py`, frontend homepage `src/webapp/frontend/app/page.tsx`. (src/scraper/api/client.py:1, src/webapp/backend/app/main.py:1, src/webapp/frontend/app/page.tsx:6)
- **Core Modules:** `src/scraper/html/` (XPath wrappers), `src/scraper/parsers/` (type conversion), `src/scraper/services/` (HTTP + parsing services), `src/scraper/output/` (JSON/CSV writers), `src/scraper/common/data.py` (domain enums). (src/scraper/html/box_scores.py:6, src/scraper/parsers/box_scores.py:54, src/scraper/services/http.py:13, src/scraper/output/writers.py:135, src/scraper/common/data.py:41)
- **Data Flow:** Client builds HTTPService + ParserService, HTTPService fetches HTML and page wrappers, ParserService converts raw strings to typed values, OutputService serializes JSON/CSV. (src/scraper/api/client.py:5, src/scraper/api/client.py:41, src/scraper/services/http.py:13, src/scraper/parsers/box_scores.py:59, src/scraper/output/service.py:6, src/scraper/output/writers.py:135)

### Coupling Analysis
- **Scraper parsing stack:** HTTPService depends on ParserService and HTML wrappers; changes in parser outputs or wrapper APIs will affect HTTPService consumers. (src/scraper/services/http.py:13, src/scraper/services/parsing.py:44)
- **Webapp ingestion:** Scraper integration relies on `sys.path` injection and direct `src.scraper` imports; path or API signature changes will break ingestion. (src/webapp/backend/app/ingestion/scraper_service.py:15, src/webapp/backend/app/ingestion/scraper_service.py:17)
- **Frontend API base:** Next.js rewrites fall back to `http://localhost:8000/api/v1` when `NEXT_PUBLIC_API_URL` is unset. (src/webapp/frontend/next.config.js:19)
- **Search fallback:** SearchService prefers Meilisearch and falls back to DB on failure, changing latency/consistency when Meilisearch is down. (src/webapp/backend/app/services/search_service.py:3, src/webapp/backend/app/services/search_service.py:90)

## Dos and Don'ts

### Do
- Use enums from `src/scraper/common/data.py` instead of raw strings. (src/scraper/common/data.py:9)
- Keep HTML wrappers using XPath and return raw strings. (src/scraper/html/box_scores.py:6)
- Convert raw strings to typed values in parsers. (src/scraper/parsers/box_scores.py:59)
- Validate fixtures immediately after scraping. (docs/scraping-guide.md:212)
- Use `requests_mock` for integration tests. (tests/integration/client/test_search.py:6, tests/integration/client/test_search.py:22)

### Don't
- Run multiple scraper instances simultaneously. (docs/scraping-guide.md:217)
- Modify fixtures manually without re-validating. (docs/scraping-guide.md:220)

## Testing Strategy

### Test Types
- **Unit Tests:** `tests/unit/` (unittest-based). (tests/unit/test_http_service.py:1)
- **Integration Tests:** `tests/integration/` with HTML fixtures. (tests/integration/parsers/test_parse_draft.py:21)
- **E2E Tests:** `tests/end to end/` with VCR recordings. (tests/end to end/test_client.py:26)

### Running Tests

```bash
# Run all tests (tests/CLAUDE.md:47)
uv run pytest

# Run single test file (tests/CLAUDE.md:59)
uv run pytest tests/unit/parsers/test_team_totals_parser.py -v

# Run with coverage (tests/CLAUDE.md:65)
uv run pytest --cov=src/scraper --cov-report=term-missing
```

## Good Examples
- **Facade API:** See `src/scraper/api/client.py:44` (public client functions).
- **DOM Wrapper:** See `src/scraper/html/box_scores.py:19` (BoxScoresPage).
- **Parser:** See `src/scraper/parsers/box_scores.py:54` (PlayerBoxScoresParser).
- **Backend Service:** See `src/webapp/backend/app/services/search_service.py:22` (SearchService).
- **Frontend Page:** See `src/webapp/frontend/app/page.tsx:6` (HomePage).

## Legacy/Avoid
- Avoid patterns in: `docs/scraping-guide.md:217` - Running multiple scraper instances simultaneously.
- Avoid patterns in: `docs/scraping-guide.md:220` - Modifying fixtures manually without re-validating.

## Security & Compliance

### Secrets Handling
- Backend settings load environment variables from `.env`. (src/webapp/backend/app/core/config.py:11)
- `.env.example` documents required secrets (DATABASE_URL, JWT_SECRET_KEY, etc.). (src/webapp/backend/.env.example:2)
- JWT secret is required and validated for length. (src/webapp/backend/app/core/config.py:32, src/webapp/backend/app/core/config.py:46)

### License
- **Type:** MIT. (pyproject.toml:11)
- **Location:** `pyproject.toml`. (pyproject.toml:11)

## Agent Guardrails

### Allowed Without Asking
> TODO: Repo does not document agent-specific allowances.

### Ask Before Doing
> TODO: Repo does not document agent-specific approval rules.

### Files Never to Modify
- `tests/integration/files/**` - Fixture edits require re-validation. (docs/scraping-guide.md:220)

## Unknowns & TODOs
> TODO: Confirm any additional agent guardrails or protected files beyond fixture validation guidance.

## Further Reading
- `docs/scraping-guide.md` (docs/scraping-guide.md:1)
- `src/webapp/README.md` (src/webapp/README.md:1)
- `src/webapp/docs/data-ingestion.md` (src/webapp/docs/data-ingestion.md:1)
