# TESTING KNOWLEDGE BASE

**Context:** QA strategy and test suite for the scraper

See root [`AGENTS.md`](../AGENTS.md) for project-wide conventions.
See [`PLAN.md`](../PLAN.md) for the current project goal and roadmap.

## Overview

Three-tier testing strategy optimized for speed (unit), correctness (integration), and reliability
(end-to-end). Tests focus on the scraper library in `src/scraper/`.

## Structure

```
tests/
├── unit/                    # Fast (<1s). Mocked HTTP. Isolated component tests.
│   ├── client/              # Client API tests
│   ├── html/                # HTML wrapper tests
│   ├── output/              # Output formatting tests
│   └── parsers/             # Parser logic tests
├── integration/             # Medium. Local HTML fixtures. Full pipeline tests.
│   ├── client/              # Client integration tests
│   ├── files/               # Source HTML fixtures from basketball-reference.com
│   ├── html/                # HTML parsing tests with fixtures
│   ├── output/              # Output integration tests
│   │   ├── expected/        # Expected JSON/CSV outputs (frozen)
│   │   └── generated/       # Generated outputs (gitignored)
│   └── parsers/             # Parser tests with fixtures
└── end to end/              # Slow. Live HTTP calls. Site structure validation.
    ├── cassettes/           # VCR cassettes for recorded HTTP responses
    └── output/              # E2E expected outputs
```

## Test Strategy

| Tier | When to Run | Purpose | HTTP |
|------|------------|---------|------|
| Unit | Every commit | Verify parser logic, data transforms, error handling | Mocked |
| Integration | PRs | Ensure HTML parsing works against known fixtures | `requests_mock` |
| End-to-End | Nightly/Manual | Guard against external site changes | Live calls |

## Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# End-to-end tests only (WARNING: makes live HTTP calls)
uv run pytest "tests/end to end/" -v

# Single file
uv run pytest tests/unit/parsers/test_team_totals_parser.py -v

# Matching pattern
uv run pytest -k "box_score" -v

# With coverage
uv run pytest --cov=src/scraper --cov-report=term-missing
```

## Writing Unit Tests

Use `unittest.mock.patch` to mock HTTP service methods:

```python
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.scraper.common.data import Team
from src.scraper.parsers import SomeParser

class TestSomeParser(TestCase):
    def setUp(self):
        self.parser = SomeParser()

    def test_parses_valid_input(self):
        result = self.parser.parse(MagicMock(attribute="value"))
        self.assertEqual(result["key"], "expected")
```

## Writing Integration Tests

Use `requests_mock` and HTML fixtures:

```python
import requests_mock
from src.scraper.api import client

class TestPlayerBoxScores:
    @requests_mock.Mocker()
    def test_returns_box_scores(self, m):
        # Load fixture
        with open("tests/integration/files/player_box_scores/2018/1/1.html") as f:
            html_content = f.read()

        # Mock the request
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.fcgi",
            text=html_content
        )

        # Call API
        result = client.player_box_scores(day=1, month=1, year=2018)

        # Assert
        assert len(result) > 0
        assert result[0]["team"] == Team.SOME_TEAM
```

## Fixtures

### HTML Fixtures

- **Location:** `tests/integration/files/{endpoint}/{params}/`
- **Source:** Real HTML pages from basketball-reference.com
- **Naming:** Mirrors API arguments (e.g., `player_box_scores/2018/1/1.html`)
- **Important:** Never modify these files - they are frozen test data

### Expected Outputs

- **Location:** `tests/integration/output/expected/`
- **Format:** JSON and CSV files
- **Purpose:** Assert that parsing produces exact expected output
- **Usage:** `filecmp.cmp()` for file comparisons

## Adding New Tests

### For a New Parser

1. **Get HTML fixture:**
   - Visit basketball-reference.com page
   - Save HTML to `tests/integration/files/{feature}/`

2. **Create expected output:**
   - Manually verify correct parsing
   - Save JSON/CSV to `tests/integration/output/expected/`

3. **Write unit tests:**
   - Create `tests/unit/parsers/test_{parser}.py`
   - Mock dependencies, test edge cases

4. **Write integration test:**
   - Create `tests/integration/parsers/test_{feature}.py`
   - Use `requests_mock` with fixture

## Conventions

- **File Naming:** `test_{module}.py` matches source module
- **Test Classes:** Group by date/parameters (e.g., `class Test20180101`)
- **Assertions:**
  - Unit: `assertEqual`, `assertIsNone`, `assertRaises`
  - Integration: `filecmp.cmp()` for output comparison
- **Fixtures:** Always create corresponding expected output files

## Common Patterns

### Testing Date-Based Endpoints

```python
class Test20180101:
    """Tests for January 1, 2018 data."""

    @requests_mock.Mocker()
    def test_player_box_scores(self, m):
        # Load specific date fixture
        fixture_path = "tests/integration/files/player_box_scores/2018/1/1.html"
        ...
```

### Testing Enum Parsing

```python
def test_parses_team_to_enum(self):
    result = self.parser.parse_team("BOS")
    self.assertEqual(result, Team.BOSTON_CELTICS)
```

### Testing Error Cases

```python
def test_raises_on_invalid_season(self):
    with self.assertRaises(InvalidSeason):
        client.season_schedule(season_end_year=1800)
```

## Files Never to Modify

- `tests/integration/files/**/*.html` - Frozen HTML fixtures
- `tests/integration/output/expected/**` - Frozen expected outputs
- `tests/end to end/cassettes/**/*.yaml` - VCR cassettes
