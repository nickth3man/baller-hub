"""
basketball-reference-scraper
============================

A Python client for scraping stats from basketball-reference.com.

ARCHITECTURE OVERVIEW
---------------------

This project follows a 3-tier pipeline architecture to separate concerns:

1. **Client (Facade)**:
   - Located in `src/client.py`.
   - The public API entry point (e.g., `player_box_scores()`).
   - Orchestrates the flow but contains no logic.

2. **HTTPService (Orchestrator)**:
   - Located in `src/http_service.py`.
   - Handles URL construction, HTTP requests (via `requests.Session`), and caching.
   - Fetches HTML and passes it to the parsing layer.

3. **Parsing Layer (Data Extraction)**:
   - Split into two distinct parts:
     a. **HTML Wrappers (`src/html/`)**:
        - Know *where* data is (DOM structure, XPath).
        - Return RAW STRINGS only.
        - Example: `row.made_field_goals` -> "12"
     b. **Parsers (`src/parsers/`)**:
        - Know *what* data means (Business logic).
        - Convert strings to types (`int`, `float`, `Team` enum).
        - Example: `str_to_int("12")` -> 12

KEY CONCEPTS
------------

- **lxml**: We use `lxml` instead of `BeautifulSoup` for performance and XPath support.
  Processing season-long tables requires the speed of C-based parsing.
- **Box Score**: A statistical summary of a single game (Points, Rebounds, Assists).
- **Play-by-Play**: A chronological log of every event in a game.
- **PACE**: Estimate of possessions per 48 minutes.
- **True Shooting % (TS%)**: Measure of shooting efficiency taking into account field goals,
  3-point field goals, and free throws.

USAGE
-----

    from basketball_reference_scraper import client

    # Get box scores for a specific date
    client.player_box_scores(day=1, month=1, year=2024)
"""
