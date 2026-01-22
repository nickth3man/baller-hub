# src/scraper AGENTS.md

**Context:** Data extraction engine (Python).
**Parent:** `../../AGENTS.md`

## STRUCTURE
```
scraper/
├── api/             # Public facade (client.py)
├── html/            # XPath wrappers
├── parsers/         # String -> Type conversion
├── services/        # HTTP & Parsing orchestration
└── output/          # CSV/JSON writers
```

## COMMANDS
```bash
# Scrape Fixtures
uv run python -m src.scraper.scripts.scrape_fixtures.main

# Validate
uv run python src/scraper/scripts/validate_fixtures.py
```

## CONVENTIONS
- **HTML:** Wrappers return raw strings; Logic uses XPath.
- **Parsers:** Pure functions (Input: HTML wrapper -> Output: Pydantic/TypedDict).
- **Validation:** Validate fixtures immediately after scraping.
- **Data:** Use enums from `common/data.py`.

## ANTI-PATTERNS
- Modifying `tests/integration/files` manually (must re-scrape).
- Network calls inside Parsers (keep them pure).
