# tests AGENTS.md

**Context:** Test suite (Unit, Integration, E2E).
**Parent:** `../AGENTS.md`

## STRUCTURE
```
tests/
├── unit/            # Isolated logic (fast)
├── integration/     # Uses HTML fixtures (no network)
└── end to end/      # Uses VCR cassettes (network/mock)
```

## COMMANDS
```bash
# Unit
uv run pytest tests/unit/

# Integration
uv run pytest tests/integration/

# E2E
uv run pytest "tests/end to end/"
```

## CONVENTIONS
- **Fixtures:** `tests/integration/files/` (Frozen HTML).
- **Network:** Integration = `requests_mock`; E2E = `vcr`.
- **Modifications:** Never edit fixtures manually; use scraper scripts.

## FILES NEVER TO MODIFY
- `tests/integration/files/**/*.html`
- `tests/end to end/cassettes/**/*.yaml`
