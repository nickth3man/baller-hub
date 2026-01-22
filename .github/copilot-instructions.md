# GitHub Copilot Instructions

## Project Summary

Baller Hub is a basketball-reference.com clone with a Python web scraper (lxml-based) and full-stack web application (FastAPI backend + Next.js 15 frontend). This monorepo contains both scraping infrastructure and a production-ready web application.

## Quick Start

**Prerequisites:** Python 3.12+, uv package manager, Node.js (for frontend)

```bash
# Install Python dependencies
uv sync

# Install frontend dependencies
cd src/webapp/frontend && npm install
```

## Build & Validation Commands

### Python (Scraper & Backend)

**ALWAYS run these commands before committing Python code:**

```bash
# Format code (fixes issues automatically)
uv run ruff format .

# Lint code (must pass with no errors)
uv run ruff check .

# Type check (must pass with no errors)
uv run ty check .

# Run tests (must pass)
uv run pytest
```

**For faster iteration on single files:**

```bash
# Type check single file
uv run ty check path/to/file.py

# Lint single file
uv run ruff check path/to/file.py

# Test single file
uv run pytest tests/unit/path/to/test_file.py -v
```

**Important:** File-scoped commands are preferred for fast feedback during development.

### Frontend (Next.js)

```bash
cd src/webapp/frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build production
npm run build

# Lint and type check
npm run lint
```

### Full Stack (Docker)

```bash
cd src/webapp

# Start all services (PostgreSQL, Redis, FastAPI, Next.js)
docker compose up -d

# Stop all services
docker compose down
```

## Critical Build Requirements

### Python Dependencies

- **ALWAYS run `uv sync`** after pulling changes or modifying `pyproject.toml`
- Dependencies are locked in `uv.lock` - DO NOT manually modify this file
- Use `uv add <package>` to add new dependencies, never edit `pyproject.toml` directly for dependencies

### Python Code Standards

- **All imports MUST be absolute** (e.g., `from src.scraper.common.data import Team`)
- **Never use relative imports** (e.g., `from ..common import Team` is forbidden)
- **Always use enums** from `src.scraper.common.data` for Team, Position, League
- **Never use raw strings** for teams, positions, or leagues
- **All HTML parsing uses lxml** (xpath selectors), never BeautifulSoup

### Testing Requirements

- Three-tier test suite: unit (mocked), integration (fixtures), end-to-end (live HTTP)
- **Integration tests require HTML fixtures** in `tests/integration/files/`
- **Never modify frozen fixtures** in `tests/integration/files/*.html`
- Use `@requests_mock.Mocker()` for integration tests
- Use `unittest.mock.patch` for unit tests

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and PR:

1. `uv sync` - Install dependencies
2. `uv run ruff check .` - Lint check
3. `uv run ty check .` - Type check
4. `uv run pytest` - Full test suite

**All checks must pass** before merging. Run these locally to catch issues early.

## Repository Layout

```
.
├── src/scraper/          # Python scraping library
│   ├── api/client.py     # Public API facade
│   ├── html/             # DOM wrappers (lxml xpath)
│   ├── parsers/          # Type conversion logic
│   ├── services/         # HTTP, caching, rate limiting
│   ├── output/           # JSON/CSV serialization
│   └── common/data.py    # Source of truth for enums
├── src/webapp/
│   ├── backend/          # FastAPI REST API
│   └── frontend/         # Next.js 15 App Router
├── tests/
│   ├── unit/             # Fast, mocked tests
│   ├── integration/      # Local fixture tests
│   │   └── files/        # Frozen HTML fixtures
│   └── end to end/       # Live HTTP tests
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## Key Configuration Files

- **pyproject.toml** - Python dependencies, ruff/ty/pytest config
- **uv.lock** - Locked Python dependencies (generated, DO NOT edit)
- **.coveragerc** - Coverage configuration
- **.pre-commit-config.yaml** - Pre-commit hooks
- **src/webapp/backend/.env.example** - Environment variable template

## Common Issues & Solutions

### "Module not found" errors
- Run `uv sync` to install dependencies
- Check imports are absolute, not relative
- Verify `PYTHONPATH` includes project root

### Type check failures
- Run `uv run ty check path/to/file.py` for specific file
- Check enum usage (Team, Position, League from `src.scraper.common.data`)
- Ensure type hints are present (ty is strict)

### Test failures
- Check if HTML fixtures need updating in `tests/integration/files/`
- Run single test with `-v` flag for verbose output
- Verify mocks are properly configured for unit tests

### Ruff formatting conflicts
- Run `uv run ruff format .` to auto-fix formatting
- Check `.ruff.toml` or `pyproject.toml` for configuration
- Line length is 88 characters (Python), 4-space indentation

## Architecture Principles

### Scraper Architecture
- **HTML wrappers** (`src/scraper/html/*.py`) - Return raw strings, no type conversion
- **Parsers** (`src/scraper/parsers/*.py`) - Convert strings to typed values
- **Services** (`src/scraper/services/*.py`) - HTTP fetching, caching, rate limiting
- **Output** (`src/scraper/output/*.py`) - JSON/CSV serialization

### Naming Patterns
- HTML wrappers: `{Entity}Page`, `{Entity}Table`, `{Entity}Row`
- Parsers: `{Entity}Parser`
- Python: snake_case for functions/variables, PascalCase for classes
- TypeScript: camelCase for functions/variables, PascalCase for components/types

### Data Flow
1. User calls `client.py` function (e.g., `player_box_scores()`)
2. `HTTPService` fetches HTML from basketball-reference.com
3. Response wrapped in lxml tree, passed to page wrapper
4. `ParserService` extracts data using parsers
5. `OutputService` formats output (JSON, CSV, or dict)

## Files Never to Modify

- `uv.lock`, `poetry.lock`, `package-lock.json` (generated lock files)
- `tests/integration/files/*.html` (frozen HTML fixtures)
- `tests/integration/output/expected/` (frozen expected outputs)
- `raw-data/*.csv` (source data files)

## Security Guidelines

- **Never commit secrets** - Use `.env` files (not tracked)
- Check `.secrets.baseline` for known secrets patterns
- Pre-commit hooks run `detect-secrets` scan
- Environment variables template at `src/webapp/backend/.env.example`

## Performance Tips

- Use file-scoped commands for fast feedback
- Run specific tests instead of full suite during development
- Use `pytest -k "pattern"` to run matching tests
- Integration tests are faster than end-to-end tests

## Further Documentation

For detailed information, see:
- `AGENTS.md` / `CLAUDE.md` - Comprehensive agent instructions
- `PLAN.md` - Active roadmap and implementation priorities
- `README.md` - Project overview
- `src/scraper/AGENTS.md` - Scraper-specific details
- `tests/AGENTS.md` - Testing strategy details
- `src/webapp/AGENTS.md` - Web application details
- `docs/` directory - Full documentation, specs, and blueprints
