# tests AGENTS.md

**Generated:** 2026-01-22
**Context:** Global Test Suite.

## OVERVIEW
The centralized testing repository for the entire monorepo, covering unit, integration, and end-to-end scenarios.

## FOLDER STRUCTURE
- `unit/`: Fast, isolated tests mocking all external dependencies.
- `integration/`: Tests using frozen HTML fixtures to verify scraping logic without network.
- `end to end/`: Full system tests using VCR cassettes to record/replay network interactions.

## CORE BEHAVIORS & PATTERNS
- **Fixture-Based**: Integration tests rely on `tests/integration/files/` (frozen HTML) to ensure determinism.
- **Network Mocking**: `requests_mock` for integration, `vcrpy` for end-to-end.
- **Separation**: Tests are separated by type to allow running specific subsets (e.g., only fast unit tests).

## CONVENTIONS
- **Commands**: `uv run pytest tests/unit`, `uv run pytest tests/integration`, `uv run pytest tests/end\ to\ end`.
- **Naming**: Test files must start with `test_`.
- **Markers**: Use pytest markers for slow tests or specific features.

## WORKING AGREEMENTS
- **Immutable Fixtures**: Never manually edit HTML fixtures. Use the scraper scripts to regenerate them.
- **Cassette Management**: Re-record VCR cassettes only when external API behavior changes.
- **Coverage**: New features must include corresponding unit tests.
