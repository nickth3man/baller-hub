# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Structure:** Monorepo (Scraper + Webapp)

## OVERVIEW
Basketball Reference clone. Python scraper + FastAPI backend + Next.js frontend.

## STRUCTURE
```
./
├── src/
│   ├── scraper/     # Core library (See src/scraper/AGENTS.md)
│   └── webapp/      # Full stack app (See src/webapp/AGENTS.md)
│       ├── backend/ # FastAPI (See src/webapp/backend/AGENTS.md)
│       └── frontend/# Next.js (See src/webapp/frontend/AGENTS.md)
├── tests/           # Global suite (See tests/AGENTS.md)
└── docs/            # Project documentation
```

## WHERE TO LOOK
| Task | Location | Documentation |
|------|----------|---------------|
| **Scraping Logic** | `src/scraper/` | `src/scraper/AGENTS.md` |
| **API Endpoints** | `src/webapp/backend/` | `src/webapp/backend/AGENTS.md` |
| **UI Components** | `src/webapp/frontend/` | `src/webapp/frontend/AGENTS.md` |
| **Testing** | `tests/` | `tests/AGENTS.md` |

## COMMANDS (GLOBAL)
```bash
# Install Dependencies
uv sync

# Run Tests
uv run pytest

# Lint/Type Check
uv run ruff check .
uv run ty check .
```

## CODE MAP
- **Entry Points:** `src/scraper/api/client.py` (Lib), `src/webapp/backend/app/main.py` (API), `src/webapp/frontend/app/page.tsx` (UI).
- **Key Configs:** `pyproject.toml` (Python), `src/webapp/frontend/package.json` (JS).

## CONVENTIONS
- **Python:** Snake_case, typed (beartype/mypy-friendly), ruff format.
- **TS/JS:** PascalCase components, prettier format.
- **Git:** Atomic commits, descriptive messages.

## NOTES
- **State:** Transitioning to `src/` root structure.
- **Dependency Manager:** `uv` is the source of truth for Python.
