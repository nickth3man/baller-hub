# PROJECT KNOWLEDGE BASE

**Context**: Pure Data Transformers
**Focus**: Data Cleaning, Normalization, Structured Output

## OVERVIEW
This directory contains "Parsers" that transform raw strings from `html` wrappers into structured, typed Python dictionaries. These are pure functions or stateless classes that encapsulate business logic for data interpretation.

## FOLDER STRUCTURE
- `base.py`: Abstract base classes defining the parser interface.
- `*.py`: Domain-specific parsers matching the `html` directory structure.

## CORE BEHAVIORS & PATTERNS
- **Composition**: Parsers compose extraction logic. `BoxScoreParser` might use `TeamStatsParser`.
- **Dependency Injection**: The `ParserService` injects dependencies. Parsers should accept configuration in `__init__`.
- **Pure Transformation**: Input is an `html` wrapper object; Output is a `dict` or `list[dict]`.

## CONVENTIONS
- **Return Types**: `dict` or `list[dict]`. Pydantic models are used at the boundary, but parsers return dicts for flexibility.
- **Type Conversion**: This is the place to convert `"1,234"` to `1234` (int) or `"2023-10-25"` to `datetime`.
- **No I/O**: Parsers MUST NOT make network calls or database queries. They operate solely on the input wrapper.

## WORKING AGREEMENTS
- **Idempotency**: Parsing the same input twice must yield the same output.
- **Validation**: Raise specific errors if essential data is missing, but tolerate optional missing fields (return `None`).
- **Separation of Concerns**: If the layout changes, fix `src/scraper/html`. If the data format requirements change, fix `src/scraper/parsers`.
