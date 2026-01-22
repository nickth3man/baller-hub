# src/scraper AGENTS.md

**Context:** Core scraping library for basketball-reference.com data extraction. (src/scraper/api/client.py:1)
**Override Justification:** Scraper has fixture scraping/validation commands and rules not covered at root. (docs/scraping-guide.md:16, docs/scraping-guide.md:19, docs/scraping-guide.md:212)

See root `../../AGENTS.md` for project-wide conventions.

## Overview
Scraper pipeline centers on HTTPService + ParserService and outputs JSON/CSV via OutputService. (src/scraper/api/client.py:5, src/scraper/output/service.py:6)

## Commands (Overrides)

```bash
# Scrape fixtures (docs/scraping-guide.md:16)
uv run python -m src.scraper.scripts.scrape_fixtures.main

# Validate fixtures (docs/scraping-guide.md:19)
uv run python src/scraper/scripts/validate_fixtures.py

# Resume from checkpoint (docs/scraping-guide.md:22)
uv run python -m src.scraper.scripts.scrape_fixtures.main --resume
```

## Conventions (Overrides)
- HTML wrappers use XPath and return raw strings. (src/scraper/html/box_scores.py:6)
- Validate fixtures immediately after scraping. (docs/scraping-guide.md:212)

## Files Never to Modify
- `tests/integration/files/**` - Fixture edits require re-validation. (docs/scraping-guide.md:220)

## Unknowns & TODOs
> TODO: Confirm any scraper-specific protected files beyond fixture guidance.
