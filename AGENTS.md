# AGENTS.md

## Project Overview

Baller Hub is a basketball-reference.com clone consisting of a Python web scraper that extracts NBA
data and a full-stack web application (FastAPI backend + Next.js frontend) that serves it. The
scraper uses `lxml` for fast HTML parsing and outputs JSON/CSV. The webapp stores scraped data in
PostgreSQL and provides REST APIs for a modern React frontend.

## Repository Structure

- **src/scraper/** - Core scraping library: HTML parsing, data extraction, JSON/CSV output
- **src/webapp/backend/** - FastAPI REST API with PostgreSQL, Redis caching, Celery tasks
- **src/webapp/frontend/** - Next.js 15 App Router frontend with Tailwind CSS
- **tests/** - Three-tier test suite: unit (mocked), integration (fixtures), end-to-end (live HTTP)
- **scripts/** - Utility scripts for fixture validation and data rescraping
- **docs/** - Project documentation, specs, and strategy blueprints
- **raw-data/** - CSV data files for reference

## Tech Stack

- **Language(s):** Python 3.12+ (scraper/backend), TypeScript 5.7 (frontend)
- **Framework(s):** FastAPI 0.115+, Next.js 15, SQLModel ORM
- **Package Manager:** uv (Python), npm (frontend)
- **Key Libraries:**
  - Scraper: lxml, requests, pytz
  - Backend: uvicorn, asyncpg, alembic, redis, meilisearch, celery
  - Frontend: React 18, TanStack Query, Zustand, Recharts, Tailwind CSS

## Build & Development Commands

### File-Scoped Commands (Preferred for Fast Feedback)

```bash
# Type check single file
uv run ty check path/to/file.py

# Lint single file
uv run ruff check path/to/file.py

# Format single file
uv run ruff format path/to/file.py

# Test single file
uv run pytest tests/unit/path/to/test_file.py -v
```

### Project-Wide Commands (Use Sparingly)

```bash
# Install dependencies
uv sync

# Run scraper tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/scraper --cov-report=term-missing

# Full lint
uv run ruff check .

# Full format
uv run ruff format .

# Full type check
uv run ty check .

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Webapp Commands

```bash
# Backend - start dev server
cd src/webapp/backend && uv run uvicorn app.main:app --reload

# Frontend - install deps and start
cd src/webapp/frontend && npm install && npm run dev

# Full stack with Docker
cd src/webapp && docker compose up -d
```

## Code Style & Conventions

### Formatting

- **Indentation:** 4 spaces (Python), 2 spaces (TypeScript/JSON)
- **Formatter:** ruff format (Python), prettier (TypeScript)
- **Line Length:** 88 characters (Python), default (TypeScript)

### Naming Conventions

- **Variables/Functions:** snake_case (Python), camelCase (TypeScript)
- **Types/Classes:** PascalCase (both)
- **Constants:** SCREAMING_SNAKE_CASE (Python), SCREAMING_SNAKE_CASE (TypeScript)
- **Files:** snake_case.py (Python), PascalCase.tsx or kebab-case.ts (TypeScript)

### Import Organization

Python imports are organized by ruff's isort rules:
1. Standard library imports
2. Third-party imports
3. First-party imports (known: `src.scraper`, `app`)

All imports must be **absolute** (e.g., `from src.scraper.common.data import Team`).

## Architecture Notes

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           User / Frontend                            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (REST API)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │  Endpoints  │→ │  Services   │→ │   Models    │→ │ PostgreSQL │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Scraper Integration                       │    │
│  │  client.py → HTTPService → ParserService → OutputService     │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Components

- **Entry Point(s):**
  - Scraper: `src/scraper/api/client.py` (Facade API)
  - Backend: `src/webapp/backend/app/main.py` (FastAPI app)
  - Frontend: `src/webapp/frontend/app/page.tsx` (Next.js home)

- **Core Modules:**
  - `src/scraper/html/` - DOM wrappers using lxml xpath selectors (returns raw strings)
  - `src/scraper/parsers/` - Type conversion from strings to Python types/enums
  - `src/scraper/services/` - HTTP fetching, caching, rate limiting
  - `src/scraper/output/` - JSON/CSV serialization
  - `src/scraper/common/data.py` - **Source of truth** for Team enums and mappings

- **Data Flow (Scraper):**
  1. User calls `client.py` function (e.g., `player_box_scores()`)
  2. `HTTPService` builds URL and fetches HTML from basketball-reference.com
  3. Response wrapped in `lxml` tree and passed to page wrapper (`html/*.py`)
  4. `ParserService` extracts data using parsers (`parsers/*.py`)
  5. `OutputService` formats output (JSON, CSV, or raw dict)

### Module Organization

- **Scraper:** Layer-based (html/ for DOM, parsers/ for logic, output/ for serialization)
- **Backend:** Feature-based with shared layers (api/endpoints, services, models, schemas)
- **Frontend:** App Router structure with (components)/ for shared React components

## Dos and Don'ts

### Do

- Use `Team` enum from `src.scraper.common.data` - never raw team strings
- Use absolute imports (e.g., `from src.scraper.common.data import Team`)
- Use lxml xpath for HTML element selection (fast, explicit)
- Keep HTML wrappers pure - return raw strings, no type conversion
- Keep parsers pure - only convert strings to typed values
- Add fixtures to `tests/integration/files/` for new HTML parsing tests
- Follow the naming pattern: `{Entity}Page`, `{Entity}Table`, `{Entity}Row` for HTML wrappers
- Follow the naming pattern: `{Entity}Parser` for parsers
- Use `@requests_mock.Mocker()` for integration tests
- Use `unittest.mock.patch` for unit tests

### Don't

- Use BeautifulSoup - lxml is explicitly chosen for performance
- Use raw strings for teams, positions, or leagues - use enums
- Modify `data.py` mappings without understanding the full impact
- Skip type hints - the codebase uses ty for type checking
- Commit untested HTML parsing changes - always add fixtures
- Use relative imports - always use absolute imports from `src.`
- Push without running `uv run ruff check .` and `uv run ty check .`

## Testing Strategy

### Test Types

- **Unit Tests:** `tests/unit/` - Mocked HTTP, fast (<1s). Tests parsers/components in isolation.
- **Integration Tests:** `tests/integration/` - Local HTML fixtures from `files/`. Tests full pipeline.
- **End-to-End Tests:** `tests/end to end/` - Live HTTP calls with rate limiting. Verifies site unchanged.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run single test file
uv run pytest tests/unit/parsers/test_team_totals_parser.py -v

# Run with coverage
uv run pytest --cov=src/scraper --cov-report=term-missing

# Run specific test class
uv run pytest tests/unit/html/test_schedule_page.py::TestSchedulePage -v

# Run tests matching pattern
uv run pytest -k "box_score" -v
```

### Coverage Requirements

Coverage tracked via `.coveragerc`. Excludes test files and specific patterns like
`pragma: no cover`. No explicit threshold enforced in CI but coverage reports generated.

## Good Examples

- **Facade Pattern (Public API):** See `src/scraper/api/client.py:40-86` (standings function)
- **DOM Wrapper Pattern:** See `src/scraper/html/box_scores.py:19-51` (BoxScoresPage class)
- **Parser Pattern:** See `src/scraper/parsers/box_scores.py:54-124` (PlayerBoxScoresParser)
- **Enum Usage:** See `src/scraper/common/data.py:41-93` (Team enum with deprecated teams)
- **HTTPService Pattern:** See `src/scraper/services/http.py:31-81` (session and retry logic)
- **Unit Test Structure:** See `tests/unit/parsers/test_team_totals_parser.py:1-21`
- **Integration Test Structure:** See `tests/integration/client/test_search.py:12-96`

## Legacy/Avoid

- Avoid patterns in: Old webapp structure at root `/webapp/` (migrated to `src/webapp/`)
- Avoid: Imports from root `src/` that bypass `src/scraper/` (e.g., never `from src.common`)
- Avoid: BeautifulSoup for HTML parsing - lxml is explicitly chosen for performance

## Security & Compliance

### Secrets Handling

- Environment variables stored in `.env` files (not committed)
- `.env.example` provided in `src/webapp/backend/` for reference
- `.secrets.baseline` tracks known secrets patterns to prevent accidental commits
- Never hardcode API keys, database credentials, or tokens

### Dependencies

- Pre-commit hooks run `detect-secrets` baseline scan
- ruff lint rules include security-related checks (B prefix)
- No explicit dependency audit tool configured

### License

- **Type:** MIT
- **Location:** Referenced in `pyproject.toml` and `README.md`

## Agent Guardrails

### Allowed Without Asking

- Reading any file
- Running file-scoped linting/formatting (`uv run ruff check/format path/to/file.py`)
- Running file-scoped type checking (`uv run ty check path/to/file.py`)
- Running single-file tests (`uv run pytest tests/.../test_file.py`)
- Searching code with grep/rg

### Ask Before Doing

- Installing new dependencies (modifying `pyproject.toml` or `package.json`)
- Deleting files or directories
- Modifying CI/CD configuration (`.github/workflows/`)
- Running full test suites (`uv run pytest` without file filter)
- Modifying `src/scraper/common/data.py` (source of truth for enums)
- Making changes to build configuration
- Creating or pushing git commits
- Modifying Docker configuration

### Files Never to Modify

- `uv.lock`, `poetry.lock`, `package-lock.json` (generated lock files)
- `.git/` directory
- `tests/integration/files/*.html` (frozen HTML fixtures)
- `tests/integration/output/expected/` (frozen expected outputs)
- `.cache/` directories
- `raw-data/` CSV files (source data)

## Current Project Goal

See [`PLAN.md`](PLAN.md) for the active roadmap, milestones, and implementation priorities.

## Further Reading

- **Scraper Details:** `src/scraper/AGENTS.md`
- **Testing Strategy:** `tests/AGENTS.md`
- **Webapp Architecture:** `src/webapp/README.md`
- **API Reference:** `docs/reference/`
- **Specifications:** `docs/specs/`
