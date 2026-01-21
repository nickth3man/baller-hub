#!/bin/bash
# Wrapper script to run scrape_fixtures without VIRTUAL_ENV conflicts
# This ensures uv manages the environment without interference

# Unset VIRTUAL_ENV to let uv manage the environment
unset VIRTUAL_ENV

# Run the script with uv
uv run python -m src.scraper.scripts.scrape_fixtures.main "$@"
