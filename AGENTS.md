# PROJECT KNOWLEDGE BASE

## OVERVIEW
Baller Hub is a Basketball Reference clone with a Python scraper core, FastAPI backend, and Next.js frontend managed as a monorepo.

## STRUCTURE
- `src/`: Shared source root.
  - `scraper/`: Data extraction logic.
  - `webapp/`: Web application (Backend + Frontend).
- `tests/`: Global test suite.

## WHERE TO LOOK
| Task | Component | Reference |
|------|-----------|-----------|
| Data Extraction, Parsing | Scraper | `src/scraper/AGENTS.md` |
| API, Database, Backend | Webapp Backend | `src/webapp/backend/AGENTS.md` |
| UI, Client-side Logic | Webapp Frontend | `src/webapp/frontend/AGENTS.md` |
| General Webapp Arch | Webapp Root | `src/webapp/AGENTS.md` |

## CONVENTIONS
- **Management**: `uv` for Python (root workspace), `npm` for Frontend.
- **Typing**: Strict Python (`mypy`/`beartype`) and TypeScript strict mode.
- **Style**: `ruff` (Python), `prettier` (TS/JS).
- **Git**: Atomic commits, conventional messages.

## COMMANDS
- **Python**: `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run ty check`
- **Frontend**: `npm install`, `npm run dev`, `npm run lint`

## NOTES
- **Monorepo**: Respect `src/` root. Do not create top-level code dirs.
- **Deps**: Python deps are centralized in `pyproject.toml` (root).
