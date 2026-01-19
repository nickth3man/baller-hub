# TESTING KNOWLEDGE BASE

**Generated:** 2026-01-18
**Context:** QA Strategy and Test Suite

## OVERVIEW
Three-tier testing strategy focusing on speed (unit), correctness (integration), and reliability (end-to-end).

## STRUCTURE
```
tests/
├── unit/               # Fast (<1s). Mocked HTTP. Tests parsers/components in isolation.
├── integration/        # Medium. Local HTML fixtures. Tests full scraping pipeline.
│   ├── files/          # Source HTML pages saved from basketball-reference.com
│   └── output/         # Expected JSON/CSV outputs for assertions
└── end to end/         # Slow. Live HTTP calls. Verifies site structure unchanged.
```

## STRATEGY
1. **Unit Tests**: Every commit. Verify parser logic, data transformation, error handling.
2. **Integration Tests**: PRs. Ensure HTML parsing works against known static fixtures.
   - Uses `requests_mock` to serve HTML from `files/`
   - Validates output matches expected JSON/CSV
3. **End-to-End**: Scheduled/Nightly. Guards against external API changes.

## FIXTURES
- **Source**: Real HTML pages scraped from basketball-reference.com
- **Location**: `tests/integration/files/{endpoint}/{params}/`
- **Naming**: Mirrors API arguments (e.g., `player_box_scores/2018/1/1.html`)
- **Utilities**: Use `SeasonScheduleMocker` decorator for schedule-related tests

## CONVENTIONS
- **File Naming**: `test_{module}.py` matches source module (e.g., `test_player_box_scores.py`)
- **Test Classes**: Group by date/parameters for integration tests (e.g., `class Test20180101`)
- **Requests**:
  - Unit: `@mock.patch` HTTPService methods
  - Integration: `@requests_mock.Mocker()` decorator
  - E2E: Real network calls with `time.sleep()` rate limiting
- **Adding New Tests**:
  - Always create HTML fixture in `integration/files/`
  - Add expected output in `integration/output/expected/`
  - Use `filecmp.cmp()` for file assertions
