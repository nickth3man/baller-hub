# PROJECT KNOWLEDGE BASE

**Context**: Python Extraction Engine
**Focus**: Orchestration, Services, Output

## OVERVIEW
The `src/scraper` directory contains the core Python extraction engine for Baller Hub. It orchestrates the fetching, parsing, and structured output of basketball data. It relies on a service-oriented architecture to manage HTTP requests, rate limiting, and parsing logic.

## FOLDER STRUCTURE
- `api/`: External API clients (e.g., for fetching raw pages).
- `html/`: HTML DOM wrappers using `lxml`. **See `src/scraper/html/AGENTS.md`**.
- `parsers/`: Pure data transformers. **See `src/scraper/parsers/AGENTS.md`**.
- `services/`: Core infrastructure (HTTP, Caching, Rate Limiting, ParsingService).
- `output/`: Data serialization and writing services (CSV, JSON, DB).
- `common/`: Shared utilities and error definitions.

## CORE BEHAVIORS & PATTERNS
- **Orchestration**: The `ParsingService` (`services/parsing.py`) coordinates the flow between `html` wrappers and `parsers`.
- **Service Layer**: Infrastructure concerns (HTTP, Caching) are isolated in `services/` to keep core logic pure.
- **Output Independence**: Parsers return raw Python objects (dicts/lists); the `output/` package handles formatting.

## CONVENTIONS
- **Language**: Python 3.12+ managed by `uv`.
- **Typing**: Strict type hints required. Use `mypy` or `ty` to verify.
- **Error Handling**: Custom exceptions in `common/errors.py`.
- **Imports**: Absolute imports from `src.scraper`.

## WORKING AGREEMENTS
- **Sub-Agent Delegation**: Refer to sub-directories `html/` and `parsers/` for specific implementation details in those domains.
- **Infrastructure Changes**: Modify `services/` only when changing *how* we fetch or process, not *what* we extract.
