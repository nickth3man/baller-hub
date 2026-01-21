from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from collections.abc import Iterable
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from src.scraper.scripts.scrape_fixtures.constants import (
    DEFAULT_CHECKPOINT,
    DEFAULT_MANIFEST,
)
from src.scraper.scripts.scrape_fixtures.engine import scrape_batch
from src.scraper.scripts.scrape_fixtures.models.core.checkpoint import ScraperCheckpoint
from src.scraper.scripts.scrape_fixtures.models.core.fixtures import FixtureManifest
from src.scraper.scripts.scrape_fixtures.scraper import AsyncComprehensiveScraper

# Initialize Rich console for beautiful output
console = Console()

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, console=console),
        logging.FileHandler("scraper.log"),
    ],
)
logger = logging.getLogger("scraper")


def _check_virtual_env() -> None:
    """Check and warn about VIRTUAL_ENV path mismatches.

    If VIRTUAL_ENV is set to a different project's path, it can cause
    warnings from uv. This function detects and warns about such cases.
    """
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if not virtual_env:
        return

    # Get the current project directory
    project_root = Path(__file__).parent.parent.parent.parent.parent
    expected_venv = project_root / ".venv"

    # Normalize paths for comparison (handle Windows/Unix differences)
    virtual_env_path = Path(virtual_env).resolve()
    expected_venv_path = expected_venv.resolve()

    # Check if VIRTUAL_ENV points to a different project
    if virtual_env_path != expected_venv_path and not str(virtual_env_path).startswith(
        str(project_root.resolve())
    ):
        logger.warning(
            f"VIRTUAL_ENV is set to '{virtual_env}' which doesn't match this project. "
            f"Consider unsetting it or using the wrapper scripts (run.sh/run.bat) "
            f"to avoid uv warnings."
        )


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse command-line arguments for the scraper.

    Args:
        argv: Command-line arguments to parse

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Scrape basketball-reference fixtures."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--phase", type=str, default=None)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--impersonate", type=str, default=None)
    parser.add_argument("--min-seconds", type=float, default=3.5)
    parser.add_argument("--max-seconds", type=float, default=5.0)
    return parser.parse_args(list(argv))


async def async_main(argv: Iterable[str]) -> int:
    """Main entry point for the async scraper application.

    Loads configuration, initializes components, and executes the scraping process
    with comprehensive error handling and cleanup.

    Args:
        argv: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args(argv)
    manifest = FixtureManifest.load(args.manifest)
    checkpoint = ScraperCheckpoint.load(args.checkpoint)

    fixtures = manifest.filter_by_phase(args.phase)
    if not fixtures:
        logger.error(f"No fixtures found for phase: {args.phase}")
        return 1

    scraper = AsyncComprehensiveScraper(
        concurrency=args.concurrency,
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
        impersonate=args.impersonate,
    )

    start_time = time.monotonic()
    console.rule("[bold blue]Basketball-Reference Fixture Scraper")
    logger.info(f"Target: {len(fixtures)} fixtures")

    try:
        await scrape_batch(
            fixtures=fixtures,
            manifest=manifest,
            checkpoint=checkpoint,
            scraper=scraper,
            validate=not args.no_validate,
            skip_existing=not args.no_skip_existing,
            retry_failures=args.retry_failures,
        )
    finally:
        checkpoint.save()
        duration = time.monotonic() - start_time
        logger.info(f"Scrape finished in {duration / 60:.1f} minutes")

    return 0


if __name__ == "__main__":
    # Check for VIRTUAL_ENV mismatches before running
    _check_virtual_env()
    sys.exit(asyncio.run(async_main(sys.argv[1:])))
