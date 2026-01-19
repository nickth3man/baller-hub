# SOURCE KNOWLEDGE BASE

**Generated:** 2026-01-18
**Context:** Core library implementation

## OVERVIEW
Implementation of the scraping pipeline. Orchestrates HTTP requests, HTML parsing, data extraction, and output formatting.

## STRUCTURE
```
src/
├── client.py           # Facade pattern - single entry point for all operations
├── http_service.py     # Request handling, caching, and retries
├── parser_service.py   # Factory that binds Parsers to HTML elements
├── parsers/            # Business logic: extracts clean data from raw HTML wrappers
├── html/               # Data access: pure lxml wrappers around DOM elements
├── output/             # Presentation: Formats data (JSON, CSV)
├── data.py             # Domain: Teams, Leagues, and other constant enumerations
└── errors.py           # Domain exceptions
```

## ARCHITECTURE (DATA FLOW)
1. **User** calls `client.py` function
2. **Client** delegates to `http_service.py` to fetch content
3. **HTTP Service** returns raw bytes/text
4. **Parser Service** initializes appropriate `html/*.py` wrapper
5. **Parsers** (`src/parsers/`) extract data from HTML wrappers
6. **Output Service** serializes the extracted data

## CONVENTIONS
- **Separation of Concerns**:
  - `src/html/`: ONLY knows about DOM structure (xpath, css selectors). Returns raw strings/elements.
  - `src/parsers/`: ONLY knows about data types. Converts raw strings to ints/floats/dates.
- **Data Mappings**: `src/data.py` is the source of truth for Team IDs. Always use `Team` enum, never string literals.

## NOTES
- **Parser/HTML Pairing**: Most entities have a matched pair (e.g., `BoxScoresPage` in html -> `BoxScoresParser` in parsers).
- **Lxml**: We use `lxml` explicitly for performance. Avoid `BeautifulSoup`.
