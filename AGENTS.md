# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-18
**Commit:** e4b4ddd
**Branch:** dev

## OVERVIEW

Python web scraper for basketball-reference.com using `lxml` for HTML parsing. Provides a public API for retrieving player stats, box scores, schedules, and play-by-play data. Managed with `uv`, linted with `ruff`, type-checked with `ty`.

## STRUCTURE

```
basketball-reference-scraper/
├── src/                    # Core library
│   ├── client.py           # Public API entry point
│   ├── html/               # HTML DOM wrappers (lxml logic)
│   ├── parsers/            # Data extraction logic
│   ├── output/             # JSON/CSV serialization
│   └── data.py             # Enums & Constants
├── tests/                  # Test suite
│   ├── unit/               # Fast, mocked tests
│   ├── integration/        # Fixture-based tests
│   └── end to end/         # Live HTTP tests
├── docs/                   # MkDocs documentation
└── .github/                # CI workflows
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| **Public API** | `src/client.py` | Start here for available features |
| **Parsing Logic** | `src/html/` | DOM traversal & data extraction |
| **Data Cleaning** | `src/parsers/` | structured data formation |
| **Output Formats** | `src/output/` | CSV/JSON writers |
| **Constants** | `src/data.py` | Team enums, mappings |
| **HTTP Layer** | `src/http_service.py` | Requests & caching |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `player_box_scores` | func | `src/client.py` | Get daily stats for a player |
| `season_schedule` | func | `src/client.py` | Get full season schedule |
| `players_season_totals` | func | `src/client.py` | Get aggregated season stats |
| `play_by_play` | func | `src/client.py` | Get play-by-play data for a game |
| `HTTPService` | class | `src/http_service.py` | Handles all web requests |
| `Team` | enum | `src/data.py` | Team constants (includes deprecated) |

## CONVENTIONS

- **Imports**: Absolute imports required (e.g., `from src.data import Team`).
- **Naming**: 
  - Parsers: `{Entity}Parser`
  - HTML Wrappers: `{Entity}Page`, `{Entity}Table`
- **Error Handling**: Custom exceptions in `src/errors.py`.

## ANTI-PATTERNS

- **Deprecated Teams**: Do NOT use historical teams (e.g., `CHARLOTTE_BOBCATS`) for current season queries.
- **Relative Imports**: Avoid `from . import utils`. Use `src.utils`.
- **Formatting**: Do NOT manually format. Run `uv run ruff format src/`.

## COMMANDS

```bash
# Setup
uv sync

# Testing
uv run pytest                   # All tests
uv run pytest tests/unit        # Unit tests only
uv run pytest --cov=src         # Coverage

# Quality
uv run ruff check src/          # Lint
uv run ruff format src/         # Format
uv run ty check src/            # Type check
```

## NOTES

- **Timezones**: All times are US/Eastern.
- **Pagination**: Schedule pages are paginated by month.
- **Player IDs**: Uses `surname + first_char_firstname + 01` convention (e.g., `jamesle01`).
