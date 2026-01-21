from __future__ import annotations

import asyncio
import logging
from urllib.parse import urljoin

from courlan import normalize_url
from curl_cffi import requests
from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from src.scraper.scripts.scrape_fixtures.models.core.checkpoint import ScraperCheckpoint
from src.scraper.scripts.scrape_fixtures.models.core.fixtures import (
    FixtureManifest,
    FixtureSpec,
)
from src.scraper.scripts.scrape_fixtures.scraper import AsyncComprehensiveScraper
from src.scraper.utils.fixture_validation import (
    build_validation_context,
    validate_fixture_html,
)

logger = logging.getLogger("scraper")
console = Console()


async def scrape_batch(
    fixtures: list[FixtureSpec],
    manifest: FixtureManifest,
    checkpoint: ScraperCheckpoint,
    scraper: AsyncComprehensiveScraper,
    validate: bool,
    skip_existing: bool,
    retry_failures: bool,
) -> None:
    """Execute a batch of fixture scraping operations with progress tracking.

    Processes fixtures sequentially within concurrent slots, with checkpointing,
    validation, and comprehensive error handling.

    Args:
        fixtures: List of fixture specifications to scrape
        manifest: Fixture manifest containing base URL and output configuration
        checkpoint: Checkpoint system for resumable scraping
        scraper: Configured scraper instance with resilience features
        validate: Whether to validate HTML content after scraping
        skip_existing: Whether to skip fixtures that already exist locally
        retry_failures: Whether to retry previously failed fixtures
    """
    output_dir = manifest.output_dir

    # Use Rich progress bar with Live for real-time updates
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        DownloadColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        refresh_per_second=4,  # Update 4 times per second
    )

    task_id = progress.add_task("Scraping fixtures...", total=len(fixtures))

    with Live(progress, console=console, refresh_per_second=4):
        async with requests.AsyncSession(
            impersonate=scraper.impersonate or "chrome124",
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            },
        ) as session:
            # Fixtures run sequentially within each concurrent slot.
            for fixture in fixtures:
                # Normalize and build URL for consistent checkpoint keys.
                raw_url = urljoin(manifest.base_url, fixture.url)
                full_url = normalize_url(raw_url)
                fixture_path = output_dir / fixture.fixture_path

                # Check conditions to skip
                if checkpoint.is_completed(full_url):
                    checkpoint.mark_skipped(
                        full_url, fixture.fixture_path, "checkpointed"
                    )
                    progress.update(
                        task_id, description=f"Skipped (cached): {fixture.url}"
                    )
                    progress.advance(task_id)
                    continue

                if not retry_failures and checkpoint.should_retry_failure(full_url):
                    checkpoint.mark_skipped(
                        full_url, fixture.fixture_path, "prior_failure"
                    )
                    progress.update(
                        task_id, description=f"Skipped (failed): {fixture.url}"
                    )
                    progress.advance(task_id)
                    continue

                if skip_existing and fixture_path.exists():
                    checkpoint.mark_skipped(full_url, fixture.fixture_path, "exists")
                    progress.update(
                        task_id, description=f"Skipped (exists): {fixture.url}"
                    )
                    progress.advance(task_id)
                    continue

                try:
                    # Update progress description to show current URL
                    progress.update(task_id, description=f"Fetching: {fixture.url}")

                    response = await scraper.fetch(full_url, session)

                    # Update progress to show download status
                    progress.update(task_id, description=f"Processing: {fixture.url}")

                    if response.status_code == 200:
                        content = response.content

                        # Validate
                        if validate and fixture.validator:
                            errors = validate_fixture_html(content, fixture.validator)
                            if errors:
                                scraper.health_metrics.validation_errors += 1
                                checkpoint.mark_failed(
                                    full_url,
                                    fixture.fixture_path,
                                    f"val_fail: {errors[0]}",
                                )
                                logger.warning(
                                    "Validation failed for %s (%s)",
                                    fixture.url,
                                    fixture.validator,
                                )
                                for error in errors:
                                    logger.warning(" - %s", error)
                                context = build_validation_context(
                                    content, fixture.validator
                                )
                                logger.warning(
                                    "Validation context for %s: %s",
                                    fixture.url,
                                    context,
                                )
                                progress.advance(task_id)
                                continue

                        # Write
                        fixture_path.parent.mkdir(parents=True, exist_ok=True)
                        fixture_path.write_bytes(content)
                        checkpoint.mark_completed(full_url, fixture.fixture_path)

                        # Update progress with completion status
                        progress.update(
                            task_id, description=f"Completed: {fixture.url}"
                        )
                    else:
                        # Non-200 status codes are already recorded in scraper.fetch()
                        checkpoint.mark_failed(
                            full_url,
                            fixture.fixture_path,
                            f"http_{response.status_code}",
                        )

                except asyncio.CancelledError:
                    # Allow cancellation to propagate - don't mark as failed
                    logger.info("Scraping cancelled by user")
                    raise
                except Exception as e:
                    checkpoint.mark_failed(full_url, fixture.fixture_path, str(e))
                    progress.update(task_id, description=f"Failed: {fixture.url}")
                    if "blocked_403" in str(e) or "circuit_breaker_open" in str(e):
                        logger.error("Scraper halted due to persistent blocks")
                        checkpoint.save()
                        break

                # Save periodically to balance durability with I/O overhead.
                progress.advance(task_id)
                if checkpoint.should_save(interval_seconds=30):
                    checkpoint.save()

                    # Update progress with health status
                    health_score = scraper.health_metrics.get_health_score()
                    progress.update(
                        task_id,
                        description=f"Scraping fixtures... (Health: {health_score:.0f})",
                    )
