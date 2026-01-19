# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-18
**Commit:** e4b4ddd
**Branch:** dev

## OVERVIEW

Python web scraper for basketball-reference.com. Extracts NBA stats (box scores, schedules, player totals, play-by-play) via HTML parsing with lxml.

## STRUCTURE

```
basketball-reference-scraper/
├── src/                    # All source code (flat structure)
│   ├── client.py           # PUBLIC API - 10 functions users call
│   ├── http_service.py     # HTTP requests + URL construction
│   ├── parser_service.py   # Parser factory/orchestration
│   ├── parsers.py          # 20+ parser classes (largest file)
│   ├── html.py             # HTML element wrappers (37K, largest)
│   ├── data.py             # Enums (Team, Position, League) + mappings
│   ├── errors.py           # Custom exceptions
│   ├── utilities.py        # str_to_int, str_to_float helpers
│   └── output/             # CSV/JSON serialization
├── tests/
│   ├── unit/               # Fast, mocked tests
│   ├── integration/        # HTML file fixtures
│   └── end to end/         # Live site tests (slow)
├── scripts/                # CI shell scripts
└── docs/                   # mkdocs documentation
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new scraping endpoint | `src/client.py` | Follow existing function pattern |
| Add new data field | `src/parsers.py` → `src/html.py` | Parser extracts, html.py accesses DOM |
| Add new team/enum | `src/data.py` | Update all 3 mappings (abbrev, name, enum) |
| Fix parsing bug | `src/html.py` | Check XPath selectors |
| Add output format | `src/output/writers.py` | Extend writer classes |
| Debug HTTP issues | `src/http_service.py` | URL patterns, response handling |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `player_box_scores()` | function | client.py:39 | Daily player stats |
| `season_schedule()` | function | client.py:120 | Full season schedule |
| `players_season_totals()` | function | client.py:144 | Season stats for all players |
| `search()` | function | client.py:239 | Player search |
| `HTTPService` | class | http_service.py:11 | All HTTP logic, URL building |
| `ParserService` | class | parser_service.py | Parser factory |
| `Team` | enum | data.py:14 | All NBA teams (current + deprecated) |
| `TEAM_ABBREVIATIONS_TO_TEAM` | dict | data.py:117 | 3-letter code mapping |

## CONVENTIONS

### Import Style (NON-STANDARD)
```python
# This project uses explicit src. prefix (unusual)
from src.http_service import HTTPService
from src.data import Team, TEAM_ABBREVIATIONS_TO_TEAM

# NOT relative imports, NOT package imports
```

### Naming
- Parser classes: `{Thing}Parser` (e.g., `TeamTotalsParser`, `SecondsPlayedParser`)
- HTML wrappers: `{Page}Page`, `{Thing}Table`, `{Thing}Row`
- Test files mirror source: `test_{module}.py`

### Data Flow
```
client.py → http_service.py → parsers.py
                ↓
            html.py (DOM access)
                ↓
            data.py (enums/mappings)
```

## ANTI-PATTERNS (THIS PROJECT)

### DEPRECATED Teams
```python
# These exist for historical data - do NOT use for current season
Team.CHARLOTTE_BOBCATS      # Now CHARLOTTE_HORNETS
Team.NEW_JERSEY_NETS        # Now BROOKLYN_NETS  
Team.SEATTLE_SUPERSONICS    # Now OKLAHOMA_CITY_THUNDER
Team.VANCOUVER_GRIZZLIES    # Now MEMPHIS_GRIZZLIES
```

### Known TODOs
- `src/html.py:1066` - Complex `has_play_by_play_data` logic needs refactor
- `tests/end to end/test_client.py:203` - Dict should be dataclass

### Play-by-Play Edge Cases
`has_play_by_play_data` in html.py handles:
- Colspan=6 → start of period (skip)
- Colspan=5 → tipoff/end period (skip)
- aria-label="Time" → header row (skip)
- Missing event at 10:00 mark → basketball-reference.com bug

## UNIQUE STYLES

### Test Organization
```
tests/unit/          # Mocked, fast
tests/integration/   # HTML fixtures in tests/integration/files/
tests/end to end/    # Live HTTP (note: space in dir name)
```

### HTML Fixture Pattern
Integration tests use saved HTML in `tests/integration/files/{endpoint}/{params}/`.

### Player Identifier Convention
Player URLs use surname-first pattern: `jamesle01` for LeBron James.
`player_identifier[0]` extracts first char for URL path construction.

## COMMANDS

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit/

# Run with coverage
uv run pytest --cov=src

# Build docs
uv run mkdocs build

# Code Quality (Linting, Formatting, Type Checking)
uv run ruff check src/                    # Lint code
uv run ruff format src/                   # Format code
uv run ty check src/                      # Type check code
uv run ruff check --fix src/              # Auto-fix lint issues
```

## NOTES

### Date Format Quirks
- Schedule times: Pre-2018 uses "am/pm", 2018+ uses "a/p" suffix
- Playing time: MM:SS format even for >60 minutes (parse manually, not strptime)

### basketball-reference.com Specifics
- All times are US/Eastern timezone
- Schedule pages paginate by month
- Search can redirect directly to player page (not search results)

### Dual Lock Files
Both `poetry.lock` and `uv.lock` exist. Project migrated from Poetry to uv. Use `uv sync`.
