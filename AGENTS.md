# PROJECT KNOWLEDGE BASE: Baller Hub

**Generated:** 2026-01-20
**Branch:** dev

## OVERVIEW

Baller Hub is a basketball-reference.com clone. It consists of a core scraper and a full-stack web application.

- **Scraper**: Python web scraper using `lxml`. Located in `src/scraper/`.
- **Web App**: FastAPI backend and Next.js frontend. Located in `src/webapp/`.

## STRUCTURE

```
baller-hub/
├── src/
│   ├── scraper/            # Core scraping library
│   │   ├── api/            # Public API (client.py)
│   │   ├── html/           # HTML DOM wrappers
│   │   ├── parsers/        # Data extraction logic
│   │   ├── output/         # JSON/CSV serialization
│   │   └── common/         # Enums & Constants
│   └── webapp/             # Full-stack application
│       ├── backend/        # FastAPI API
│       └── frontend/       # Next.js UI
└── tests/                  # Test suite for scraper
```

## WHERE TO LOOK (Scraper)

| Task | Location | Notes |
|------|----------|-------|
| **Public API** | `src/scraper/api/client.py` | Start here for available features |
| **Parsing Logic** | `src/scraper/html/` | DOM traversal & data extraction |
| **Data Cleaning** | `src/scraper/parsers/` | structured data formation |
| **Output Formats** | `src/scraper/output/` | CSV/JSON writers |
| **Constants** | `src/scraper/common/data.py` | Team enums, mappings |

## CONVENTIONS

- **Imports**: Absolute imports required (e.g., `from src.scraper.common.data import Team`).
- **Structure**: All code lives under the top-level `src/` directory.

## COMMANDS

```bash
# Setup
uv sync

# Testing (Scraper)
uv run pytest

# Quality
uv run ruff check src/
uv run ruff format src/
uv run ty check src/
```
