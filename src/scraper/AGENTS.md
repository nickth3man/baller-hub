# SCRAPER KNOWLEDGE BASE

**Context:** Core scraping library for basketball-reference.com

See root [`AGENTS.md`](../../AGENTS.md) for project-wide conventions.
See [`PLAN.md`](../../PLAN.md) for the current project goal and roadmap.

## Overview

Python web scraper that extracts NBA data from basketball-reference.com. Uses `lxml` for fast HTML
parsing and provides JSON/CSV output. The `client.py` module is the single entry point for all
operations.

## Structure

```
src/scraper/
├── api/
│   └── client.py          # FACADE - single entry point for all operations
├── common/
│   ├── data.py            # SOURCE OF TRUTH - Team enums, abbreviations, mappings
│   └── errors.py          # Custom domain exceptions
├── html/                  # DOM wrappers (raw strings only)
│   ├── base_rows.py       # Base row classes
│   ├── box_scores.py      # Box score page/table wrappers
│   ├── daily.py           # Daily leaders page
│   ├── play_by_play.py    # Play-by-play page
│   ├── player.py          # Player page wrappers
│   ├── schedule.py        # Schedule page
│   ├── search.py          # Search results page
│   ├── season_totals.py   # Season totals tables
│   └── standings.py       # Standings page
├── parsers/               # Type conversion logic
│   ├── base.py            # Base parser classes
│   ├── box_scores.py      # Box score parsing
│   ├── play_by_play.py    # Play-by-play parsing
│   ├── player.py          # Player data parsing
│   ├── schedule.py        # Schedule parsing
│   ├── search.py          # Search result parsing
│   ├── standings.py       # Standings parsing
│   └── team.py            # Team data parsing
├── output/                # Serialization layer
│   ├── columns.py         # Column name constants
│   ├── fields.py          # Field formatters
│   ├── service.py         # OutputService orchestrator
│   └── writers.py         # JSON/CSV writers
├── services/              # Infrastructure services
│   ├── cache.py           # Response caching
│   ├── http.py            # HTTPService - fetches and parses HTML
│   ├── parsing.py         # ParserService - binds parsers to HTML
│   ├── rate_limiter.py    # Rate limiting for requests
│   └── url_builder.py     # URL construction
├── utils/                 # Utilities
│   ├── casting.py         # Type casting helpers
│   ├── dictionaries.py    # Dict manipulation
│   └── fixture_validation.py
└── logging_config.py      # Logging setup
```

## Architecture

**Data Flow:**
```
client.py → HTTPService → ParserService → OutputService
               │              │                │
               ▼              ▼                ▼
         Fetch HTML    html/*.py         JSON/CSV
         via requests  wrappers          or raw dict
                           │
                           ▼
                     parsers/*.py
                     (type conversion)
```

**Separation of Concerns:**
- `html/` - Knows ONLY DOM structure. Uses lxml xpath. Returns raw strings.
- `parsers/` - Knows ONLY data types. Converts strings to int/float/Date/Enum.
- `output/` - Pure presentation layer. No business logic.

## Key Patterns

### HTML Wrapper Naming

| Entity | Page | Table | Row |
|--------|------|-------|-----|
| Box Scores | `BoxScoresPage` | `StatisticsTable` | `BasicBoxScoreRow` |
| Schedule | `SchedulePage` | `ScheduleTable` | `ScheduleRow` |
| Player | `PlayerPage` | `PlayerTotalsTable` | `PlayerTotalsRow` |

### Parser Naming

Parsers match their HTML counterparts:
- `BoxScoresPage` → `BoxScoresParser`
- `PlayerSeasonBoxScoresPage` → `PlayerSeasonBoxScoresParser`

### The `data.py` Contract

`src/scraper/common/data.py` (lines 1-414) is the **source of truth** for domain constants:

```python
# Team enum - use this, never raw strings
from src.scraper.common.data import Team
team = Team.BOSTON_CELTICS  # Correct
team = "Boston Celtics"      # WRONG

# Mappings (lines 193-238)
TEAM_ABBREVIATIONS_TO_TEAM["BOS"]  # → Team.BOSTON_CELTICS
TEAM_TO_TEAM_ABBREVIATION[Team.BOSTON_CELTICS]  # → "BOS"

# All available enums: Team, Position, Outcome, Location, League, Conference, Division
```

## Commands

```bash
# Lint scraper code
uv run ruff check src/scraper/

# Format scraper code
uv run ruff format src/scraper/

# Type check scraper
uv run ty check src/scraper/

# Run scraper tests only
uv run pytest tests/ -v
```

## Adding New Endpoints

1. Add URL construction in `services/url_builder.py`
2. Add fetch method in `services/http.py`
3. Create HTML wrapper in `html/` (returns raw strings)
4. Create parser in `parsers/` (converts to typed data)
5. Add public function in `api/client.py`
6. Add column names in `output/columns.py`
7. Add tests in `tests/unit/` and `tests/integration/`

## Common Pitfalls

- **Using BeautifulSoup**: Use lxml xpath instead for performance
- **Raw team strings**: Always use `Team` enum from `data.py`
- **Type conversion in HTML wrappers**: Keep them pure - return strings only
- **Relative imports**: Use absolute imports from `src.scraper.`
