# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Structure:** Monorepo (Scraper + Webapp)

## OVERVIEW
Baller Hub is a Basketball Reference clone comprising a Python-based scraper core, a FastAPI backend, and a Next.js frontend. The project is organized as a monorepo managed by `uv` for Python and `npm` for JavaScript/TypeScript.

## FOLDER STRUCTURE
- `src/scraper/`: Core data extraction library (Python).
- `src/webapp/backend/`: FastAPI backend service (Python).
- `src/webapp/frontend/`: Next.js 15 frontend application (TypeScript).
- `tests/`: Global test suite covering unit, integration, and end-to-end scenarios.
- `docs/`: Project documentation.

## CORE BEHAVIORS & PATTERNS
- **Monorepo Architecture**: Shared Python environment via `uv`, distinct frontend management via `npm`.
- **Data Flow**: Scraper -> Raw Data -> FastAPI -> Frontend.
- **Testing Strategy**: Hierarchical testing with frozen fixtures for stability.

## CONVENTIONS
- **Python**: Strict typing (`beartype`, `mypy`/`ty`), `snake_case`, `ruff` formatting.
- **TypeScript**: `PascalCase` for components, `prettier` formatting, `npm` for dependency management.
- **Git**: Atomic commits with descriptive messages.
- **Commands**:
    - Python: `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run ty check`.
    - Frontend: `npm install`, `npm run lint`, `npm run format`.

## WORKING AGREEMENTS
- **Directory Integrity**: Respect the `src/` root structure. Do not create top-level code directories outside `src/` or `tests/`.
- **Dependency Management**: Always use `uv` for Python packages and `npm` for Node packages.
- **Documentation**: Update sub-directory `AGENTS.md` files when modifying architecture.
- **Code Search**: If you are unsure how to do something, use `gh_grep` to search code examples from GitHub.
