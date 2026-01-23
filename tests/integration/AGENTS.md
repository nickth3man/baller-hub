# FIXTURE-BASED TESTING

## OVERVIEW
Integration tests verify component interactions and parsing logic using deterministic, frozen data without making real network requests.

## FOLDER STRUCTURE
- `client/`: Tests for the public API client.
- `files/`: Frozen HTML source files used as input fixtures.
- `html/`: Tests for specific HTML page wrappers.
- `output/`: Contains `expected/` and `generated/` JSON/CSV files for assertion.
- `parsers/`: Tests for data extraction logic.

## CORE BEHAVIORS & PATTERNS
- **Network Mocking**: Uses `requests_mock` to intercept HTTP calls and serve local files.
- **Data Driven**: Inputs read from `files/`, outputs compared against `output/expected/`.
- **Validation**: Compares generated CSV/JSON byte-for-byte with expected artifacts.

## CONVENTIONS
- **Fixture Naming**: `{slug}.html` (e.g., `jamesle01.html`) or `{year}.html`.
- **Paths**: Absolute paths relative to repository root for loading files.
- **Assertion**: Use helper methods to compare file contents (ignoring timestamps if needed).

## WORKING AGREEMENTS
- **Immutable Fixtures**: **Never modify frozen fixtures manually.**
- **Regeneration**: Use scraper scripts to fetch new data if the source format changes.
- **Isolation**: Tests must not depend on external state or live APIs.
