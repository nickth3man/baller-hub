# GLOBAL TEST SUITE

## OVERVIEW
The central testing repository ensures reliability across unit, integration, and end-to-end scenarios for the Baller Hub monorepo.

## FOLDER STRUCTURE
- `unit/`: Fast, isolated tests using mocks for individual components.
- `integration/`: Fixture-based tests verifying component interactions using frozen data.
- `end to end/`: Full system tests using VCR cassettes to simulate real network interactions.

## CORE BEHAVIORS & PATTERNS
- **Unit Testing**: Strict isolation, mocking all external dependencies.
- **Integration Testing**: Deterministic verification using `requests_mock` and static HTML fixtures.
- **End-to-End**: Validates the full scraper pipeline against recorded HTTP interactions.

## CONVENTIONS
- **Naming**: `test_*.py` for test files.
- **Tools**: `pytest` for running tests, `requests_mock` for network simulation.
- **Fixtures**: Centralized in `conftest.py` or local `files/` directories.

## WORKING AGREEMENTS
- **Stability**: Never modify frozen fixtures manually; regenerate if necessary.
- **Coverage**: Ensure new features have corresponding unit and integration tests.
- **Commands**: `uv run pytest tests/` to run all tests.
