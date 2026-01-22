# Baller Hub

A basketball-reference.com clone and data infrastructure project. This repository contains the core scraping engine, backend API, and frontend web application.

## Overview

Baller Hub is a comprehensive platform designed to mirror and extend the functionality of Basketball Reference. It uses a sophisticated scraping engine to build a local data warehouse, which powers a modern web interface.

## Project Structure

The codebase is organized into a monorepo structure:

- `src/scraper/`: The core scraping library (formerly `basketball-reference-scraper`).
- `src/webapp/`: The full-stack web application (FastAPI backend + Next.js frontend).

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Setup the workspace
uv sync

# Run the web application
cd src/webapp/backend
uv run uvicorn app.main:app --reload
```

## Restructuring Plan

We are currently in the process of restructuring the repository to better support the monorepo architecture:

1.  **Rename `src/` to `scraper/`**: Transition the core library from a standalone package to a component of the hub.
2.  **Move to `src/` root**: Consolidate all application code under a top-level `src/` directory.
    -   `scraper/` -> `src/scraper/`
    -   `webapp/` -> `src/webapp/`
3.  **Update Imports**: Refactor all absolute imports to use the new package structure.

## License

MIT
