## OVERVIEW

Implementation of the scraping pipeline. Orchestrates HTTP requests, HTML parsing, data extraction, and output formatting.

## STRUCTURE

```
src/
├── client.py              # Facade - single entry point for all operations
├── http_service.py        # Request handling with `lxml` parsing
├── parser_service.py      # Factory that binds Parsers to HTML elements
├── html/                  # DOM wrappers using lxml xpath/css selectors
├── parsers/               # Business logic converting raw strings to typed data
├── output/                # JSON/CSV serialization
├── data.py                # Team enums, abbreviations, and domain constants
└── errors.py              # Custom domain exceptions
```

## ARCHITECTURE

**Data Flow:**
1. User calls `client.py` function
2. `HTTPService` fetches content from basketball-reference.com
3. Returns raw bytes → parsed to `lxml` HTML
4. `ParserService` initializes appropriate `html/*.py` wrapper
5. `ParserService` invokes parser from `parsers/` on HTML wrapper
6. `OutputService` serializes (JSON/CSV) or returns raw dicts

**Separation of Concerns:**
- **`html/`**: Knows ONLY DOM structure. Uses `lxml` xpath selectors. Returns raw strings.
- **`parsers/`**: Knows ONLY data types. Converts strings to `int`/`float`/`Date`/`Enum` using `data.py` mappings.
- **`output/`**: Pure presentation layer. No business logic.

## CONVENTIONS

**Naming:**
- HTML wrappers: `{Entity}Page`, `{Entity}Table`, `{Entity}Row`
- Parsers: `{Entity}Parser`

**Parser/HTML Pairing:**
Most entities have matched pairs:
- `BoxScoresPage` (html/) → `BoxScoresParser` (parsers/)
- `PlayerSeasonBoxScoresPage` (html/) → `PlayerSeasonBoxScoresParser` (parsers/)

**Critical: `data.py` is source of truth.**
- `Team` enum contains all 30 current teams + deprecated teams (marked clearly)
- `TEAM_ABBREVIATIONS_TO_TEAM`: maps "BOS" → `Team.BOSTON_CELTICS`
- `TEAM_TO_TEAM_ABBREVIATION`: reverse mapping for URL construction
- `DIVISIONS_TO_CONFERENCES`: maps `Division.ATLANTIC` → `Conference.EASTERN`
- **Never use string literals for teams** - always import `Team` from `src.data`

**Lxml Performance:**
We explicitly use `lxml` for speed. Avoid `BeautifulSoup`. All HTML wrappers use `html.xpath()` for element selection.
