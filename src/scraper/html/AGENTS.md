# PROJECT KNOWLEDGE BASE

**Context**: HTML Dom Wrappers (lxml)
**Focus**: DOM Traversal, XPath Encapsulation

## OVERVIEW
This directory contains classes that wrap raw HTML content using `lxml`. These classes provide a structured API to access DOM elements without performing data cleaning or type conversion. They represent the "View" of the raw data.

## FOLDER STRUCTURE
- `base_rows.py`: Mixin classes for common row patterns (e.g., `StatsRow`, `LinkRow`).
- `*.py`: Domain-specific wrappers (e.g., `player.py`, `box_scores.py`) corresponding to website pages.

## CORE BEHAVIORS & PATTERNS
- **Hierarchy**: `Page` -> `Table` -> `Row`.
    - A `Page` class wraps the entire HTML document.
    - `Page` exposes `Table` objects via properties.
    - `Table` yields `Row` objects.
- **Lazy Evaluation**: Use `@property` for XPaths to defer evaluation until access.
- **Resilience**: XPaths should be robust to layout shifts (prefer relative paths inside rows).

## CONVENTIONS
- **Return Types**: ALWAYS return `str` (or `None`). NEVER convert to `int`, `float`, or `datetime`.
- **No Business Logic**: Do not interpret data (e.g., don't calculate "Points Per Game"). Just extract the text.
- **Inheritance**: Use `base_rows.py` mixins to share common column extraction logic (e.g., `PlayerColumnMixin`).

## WORKING AGREEMENTS
- **Pure Extraction**: If you need to clean a string (strip whitespace), that's okay. If you need to parse a date, do it in `src/scraper/parsers`.
- **Selector Stability**: Use IDs and specific classes where possible. Avoid brittle absolute XPaths.
