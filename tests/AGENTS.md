# tests AGENTS.md

**Context:** Test suite covering scraper behavior across unit, integration, and end-to-end tiers. (tests/unit/test_http_service.py:1, tests/integration/parsers/test_parse_draft.py:1, tests/end to end/test_client.py:1)
**Override Justification:** Tests have tier-specific pytest commands and frozen fixture rules. (tests/CLAUDE.md:50, tests/CLAUDE.md:195)

See root `../AGENTS.md` for project-wide conventions.

## Overview
Integration tests load HTML fixtures and end-to-end tests use VCR recordings. (tests/integration/parsers/test_parse_draft.py:21, tests/end to end/test_client.py:26)

## Commands (Overrides)

```bash
# Unit tests only (tests/CLAUDE.md:50)
uv run pytest tests/unit/ -v

# Integration tests only (tests/CLAUDE.md:53)
uv run pytest tests/integration/ -v

# End-to-end tests only (tests/CLAUDE.md:56)
uv run pytest "tests/end to end/" -v
```

## Conventions (Overrides)
- Integration tests load fixtures from `tests/integration/files/`. (tests/integration/parsers/test_parse_draft.py:21)
- Integration tests use `requests_mock`. (tests/integration/client/test_search.py:22)
- End-to-end tests use `@pytest.mark.vcr`. (tests/end to end/test_client.py:26)

## Files Never to Modify
- `tests/integration/files/**/*.html` - Frozen HTML fixtures. (tests/CLAUDE.md:195)
- `tests/integration/output/expected/**` - Frozen expected outputs. (tests/CLAUDE.md:196)
- `tests/end to end/cassettes/**/*.yaml` - VCR cassettes. (tests/CLAUDE.md:197)

## Unknowns & TODOs
> TODO: Confirm whether coverage runs are required in CI beyond local use.
