# Scraping Guide (How-To)

Guide for re-scraping HTML fixtures from basketball-reference.com.

> **Source of Truth**: This document is derived from [PLAN.md](../PLAN.md).

## Overview

The scraper infrastructure uses chaos engineering principles to reliably fetch
HTML fixtures while respecting rate limits and handling failures gracefully.

## Quick Start

```bash
# Run the fixture scraper
uv run python -m src.scraper.scripts.scrape_fixtures.main

# Validate existing fixtures
uv run python src/scraper/scripts/validate_fixtures.py

# Resume from checkpoint
uv run python -m src.scraper.scripts.scrape_fixtures.main --resume
```

## Scraper Architecture

```
src/scraper/scripts/scrape_fixtures/
├── main.py              # Entry point and CLI
├── engine.py            # Scraping engine with retry logic
├── scraper.py           # URL fetching and HTML saving
├── circuit_breaker.py   # Circuit breaker for failure handling
├── constants.py         # Configuration constants
└── models/
    ├── core/
    │   ├── fixtures.py      # Fixture definitions
    │   └── checkpoint.py    # Progress tracking
    └── monitoring/
        ├── health.py        # Health metrics
        └── chaos.py         # Chaos engineering hooks
```

## Configuration

### Rate Limiting

| Setting | Value | Rationale |
|---------|-------|-----------|
| Min delay | 3.5 seconds | Respect robots.txt |
| Max delay | 5.0 seconds | Random jitter |
| Backoff base | 10 seconds | After 429 response |
| Max backoff | 300 seconds | 5 minute ceiling |

### Retry Policy

| Scenario | Max Retries | Backoff |
|----------|-------------|---------|
| Network timeout | 3 | Exponential |
| HTTP 429 (rate limit) | 5 | Exponential with Retry-After |
| HTTP 5xx | 3 | Exponential |
| HTTP 403 (blocked) | 0 | Halt immediately |
| HTTP 404 | 0 | Log and skip |

## Checkpointing

Progress is saved to `scraper_checkpoint.json` after every 10 successful fetches.

```json
{
  "completed": ["url1", "url2", ...],
  "failed": {"url3": "HTTP 404", ...},
  "current_batch": "phase_2",
  "last_updated": "2026-01-21T10:30:00Z"
}
```

### Resuming

```bash
# Auto-resume from last checkpoint
uv run python -m src.scraper.scripts.scrape_fixtures.main --resume

# Start fresh (ignores checkpoint)
uv run python -m src.scraper.scripts.scrape_fixtures.main --fresh
```

## Validation Rules

Each page type has validation rules to ensure the HTML structure is correct.

### Example Validation Rules

```python
VALIDATION_RULES = {
    'standings': {
        'required_ids': ['divs_standings_E', 'divs_standings_W'],
        'required_xpath': '//table[contains(@id, "standings")]//tbody/tr',
        'min_rows': 15,  # At least 15 teams per conference
    },
    'box_score': {
        'required_pattern': r'box-[A-Z]{3}-game-basic',
        'required_tables': 2,  # Both teams
    },
    'player_totals': {
        'required_ids': ['totals_stats'],
        'min_rows': 400,  # ~400+ players per season
    },
    'play_by_play': {
        'required_ids': ['pbp'],
        'min_rows': 100,  # At least 100 plays per game
    },
}
```

### Running Validation

```bash
# Validate all fixtures
uv run python src/scraper/scripts/validate_fixtures.py

# Validate specific directory
uv run python src/scraper/scripts/validate_fixtures.py --path tests/integration/files/standings/

# Output validation report
uv run python src/scraper/scripts/validate_fixtures.py --report validation_report.json
```

## URL Manifest

The scraper uses a manifest defining all URLs to fetch.

### Manifest Format

```python
URL_MANIFEST = [
    # (url_pattern, fixture_path, validator_key)
    ("/leagues/NBA_2024.html", "standings/2024.html", "standings"),
    ("/boxscores/202406170BOS.html", "boxscores/202406170BOS.html", "box_score"),
    # ...
]
```

### Adding New URLs

1. Add entry to `src/scraper/scripts/scrape_fixtures/models/core/fixtures.py`
2. Define validation rule in `src/scraper/scripts/validate_fixtures.py`
3. Run scraper for the specific batch

## Failure Handling

### HTTP 429 (Rate Limit)

1. Scraper pauses for `Retry-After` header value (or 60s default)
2. Exponential backoff on repeated 429s
3. Circuit breaker opens after 5 consecutive 429s
4. Save checkpoint and halt

### HTTP 403 (Blocked)

1. Immediate halt
2. Save checkpoint
3. Manual intervention required (IP rotation or cooldown)

### Network Errors

1. Retry with exponential backoff
2. After 3 failures, log and skip URL
3. Continue with remaining URLs

### Page Structure Changes

1. Validation fails on fresh scrape
2. Fixture saved with `.unvalidated` suffix
3. Manual inspection required
4. Update validator rules if needed

## Monitoring

### Console Output

```
[2026-01-21 10:30:15] Scraping: /leagues/NBA_2024.html
[2026-01-21 10:30:18] ✓ Saved: standings/2024.html (45KB, 3.2s)
[2026-01-21 10:30:22] Scraping: /boxscores/202406170BOS.html
[2026-01-21 10:30:25] ✓ Saved: boxscores/202406170BOS.html (128KB, 2.8s)
...
[2026-01-21 11:45:00] Complete: 543/543 pages (0 failed)
```

### Metrics

```python
scraper_metrics = {
    'total_pages': 543,
    'completed': 0,
    'failed': 0,
    'skipped': 0,
    'rate_limit_hits': 0,
    'avg_response_time_ms': 0,
    'errors_by_type': {},
    'validation_failures': 0,
    'estimated_time_remaining': '32 hours',
}
```

## Best Practices

### Do

- Run scraper during off-peak hours (late night US time)
- Monitor checkpoint file for progress
- Validate fixtures immediately after scraping
- Keep backups of working fixtures before re-scraping

### Don't

- Run multiple scraper instances simultaneously
- Ignore rate limit warnings
- Skip validation step
- Modify fixtures manually without re-validating

## Troubleshooting

### "Too many 429 responses"

```bash
# Wait at least 1 hour before resuming
# Consider running at different time of day
uv run python -m src.scraper.scripts.scrape_fixtures.main --resume
```

### "Validation failed for {fixture}"

```bash
# Inspect the fixture manually
cat tests/integration/files/{fixture}

# Check if page structure changed on basketball-reference.com
# Update validation rules if needed
```

### "Checkpoint corrupted"

```bash
# Start fresh (lose progress)
uv run python -m src.scraper.scripts.scrape_fixtures.main --fresh

# Or manually fix checkpoint JSON
```

## References

| Topic | Location |
|-------|----------|
| Fixture rebuild plan | [PLAN.md](../PLAN.md) |
| Fixture catalog | [fixtures.md](./fixtures.md) |
| Page type documentation | [page-types.md](./page-types.md) |
| Scraper source code | `src/scraper/scripts/scrape_fixtures/` |
