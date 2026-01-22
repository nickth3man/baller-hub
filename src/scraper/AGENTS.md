# src/scraper AGENTS.md

**Generated:** 2026-01-22
**Context:** Data extraction engine (Python).

## OVERVIEW
The core scraping library for Baller Hub, responsible for extracting data from basketball-reference.com. It uses XPath for parsing and Pydantic for data validation.

## FOLDER STRUCTURE
- `api/`: Public facade (`client.py`) for consuming applications.
- `html/`: Wrapper classes around raw HTML strings to facilitate XPath queries.
- `parsers/`: Pure functions transforming `html` wrappers into Pydantic models.
- `services/`: Orchestration logic (HTTP client, Rate Limiter, Caching).
- `output/`: Utilities for writing data to CSV/JSON.

## CORE BEHAVIORS & PATTERNS
- **Pure Parsers**: Parsing logic is strictly separated from network logic.
- **Fixture-First**: All parsers are developed and tested against frozen HTML fixtures.
- **Data Validation**: Pydantic models ensure type safety for all extracted data.

## CONVENTIONS
- **Naming**: Snake_case for Python modules and variables.
- **Type Safety**: strict `beartype` usage on public methods.
- **Imports**: Relative imports within the package are allowed, but absolute imports are preferred for clarity.

## WORKING AGREEMENTS
- **No Network in Parsers**: Parsers must never make HTTP requests.
- **Fixture Integrity**: Validate fixtures immediately after scraping (`uv run python src/scraper/scripts/validate_fixtures.py`).
- **Data Enum**: Use enums from `common/data.py` for standardizing strings (e.g., Team names).
