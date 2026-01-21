@echo off
REM Wrapper script to run scrape_fixtures without VIRTUAL_ENV conflicts
REM This ensures uv manages the environment without interference

REM Unset VIRTUAL_ENV to let uv manage the environment
set VIRTUAL_ENV=

REM Run the script with uv
uv run python -m src.scraper.scripts.scrape_fixtures.main %*
