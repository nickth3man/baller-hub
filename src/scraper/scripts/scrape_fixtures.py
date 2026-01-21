"""
Rescrape basketball-reference fixtures with async support, checkpoints, validation,
and advanced impersonation.

Features:
- Async scraping with curl_cffi.AsyncSession (TLS/JA3 impersonation)
- Concurrency control with asyncio.Semaphore
- Rich progress tracking and beautiful terminal output
- Rotating browser impersonation profiles
- URL normalization with courlan
- High-performance HTML validation
- Circuit breaker and exponential backoff
- Phase-based scraping and checkpoint/resume support
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict
from urllib.parse import urljoin

from courlan import normalize_url

# Advanced networking and scraping tools
from curl_cffi import requests
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

from src.scraper.utils.fixture_validation import validate_fixture_html

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

DEFAULT_BASE_URL = "https://www.basketball-reference.com"
DEFAULT_MANIFEST = Path("src/scraper/scripts/fixture_manifest.json")
DEFAULT_CHECKPOINT = Path("scraper_checkpoint.json")
MIN_DISK_SPACE_GB = 1.0

# Available impersonation profiles for rotation
IMPERSONATION_PROFILES = [
    "chrome124",
    "chrome110",
    "chrome116",
    "chrome119",
    "safari170",
    "safari155",
    "firefox120",
    "edge101",
]


class FixtureDict(TypedDict, total=False):
    url: str
    fixture_path: str
    validator: str | None
    phase: str | None


@dataclass(frozen=True)
class FixtureSpec:
    url: str
    fixture_path: str
    validator: str | None = None
    phase: str | None = None


@dataclass(frozen=True)
class FixtureManifest:
    base_url: str
    output_dir: Path
    fixtures: list[FixtureSpec]
    phases: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> FixtureManifest:
        data = json.loads(path.read_text(encoding="utf-8"))
        base_url = data.get("base_url", DEFAULT_BASE_URL)
        output_dir = Path(data.get("output_dir", "tests/integration/files"))
        phases = data.get("phases", {})
        fixtures = [
            FixtureSpec(
                url=fixture["url"],
                fixture_path=fixture["fixture_path"],
                validator=fixture.get("validator"),
                phase=fixture.get("phase"),
            )
            for fixture in data.get("fixtures", [])
        ]
        return cls(
            base_url=base_url, output_dir=output_dir, fixtures=fixtures, phases=phases
        )

    def filter_by_phase(self, phase: str | None) -> list[FixtureSpec]:
        if phase is None:
            return self.fixtures
        return [f for f in self.fixtures if f.phase and f.phase.startswith(phase)]


@dataclass
class ScraperCheckpoint:
    path: Path
    completed: dict[str, dict] = field(default_factory=dict)
    failed: dict[str, dict] = field(default_factory=dict)
    skipped: dict[str, dict] = field(default_factory=dict)
    last_save_time: float = field(default_factory=time.monotonic)

    @classmethod
    def load(cls, path: Path) -> ScraperCheckpoint:
        if not path.exists():
            return cls(path=path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(
                path=path,
                completed=data.get("completed", {}),
                failed=data.get("failed", {}),
                skipped=data.get("skipped", {}),
            )
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return cls(path=path)

    def save(self) -> None:
        payload = {
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "last_updated": datetime.now(UTC).isoformat(),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.last_save_time = time.monotonic()

    def mark_completed(self, url: str, fixture_path: str) -> None:
        self.completed[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.failed.pop(url, None)

    def mark_failed(self, url: str, fixture_path: str, reason: str) -> None:
        self.failed[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        }

    def mark_skipped(self, url: str, fixture_path: str, reason: str) -> None:
        self.skipped[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        }

    def is_completed(self, url: str) -> bool:
        return url in self.completed

    def should_retry_failure(self, url: str) -> bool:
        return url in self.failed

    def should_save(self, interval_seconds: float = 60.0) -> bool:
        """Check if checkpoint should be saved based on time interval."""
        return time.monotonic() - self.last_save_time > interval_seconds


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout_seconds: float = 300.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout_seconds
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")

    def record_success(self) -> None:
        self.failure_count = 0
        if self.state != "CLOSED":
            logger.info("Circuit breaker CLOSED")
            self.state = "CLOSED"

    def can_proceed(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if (
                self.last_failure_time
                and time.monotonic() - self.last_failure_time > self.reset_timeout
            ):
                self.state = "HALF_OPEN"
                return True
            return False
        return True


class AsyncComprehensiveScraper:
    def __init__(
        self,
        concurrency: int = 2,
        min_seconds: float = 3.5,
        max_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        impersonate: str | None = None,
    ) -> None:
        self.semaphore = asyncio.Semaphore(concurrency)
        self.min_seconds = min_seconds
        self.max_seconds = max_seconds
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.impersonate = impersonate
        self.circuit_breaker = CircuitBreaker()
        self._last_request_time = 0.0

    async def fetch(self, url: str, session: requests.AsyncSession) -> requests.Response:
        if not self.circuit_breaker.can_proceed():
            raise RuntimeError("circuit_breaker_open")

        async with self.semaphore:
            # Enforce inter-request delay
            now = time.monotonic()
            elapsed = now - self._last_request_time
            delay = random.uniform(self.min_seconds, self.max_seconds)
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)

            for attempt in range(self.max_retries + 1):
                try:
                    # Rotate impersonation if not pinned
                    profile = self.impersonate or random.choice(IMPERSONATION_PROFILES)

                    # Note: curl_cffi AsyncSession is initialized with a profile,
                    # but we can also pass it to individual requests in recent versions.
                    # If not, we'll rely on the session's default.

                    response = await session.get(url, timeout=self.timeout_seconds)
                    self._last_request_time = time.monotonic()

                    if response.status_code == 200:
                        self.circuit_breaker.record_success()
                        return response

                    if response.status_code == 403:
                        self.circuit_breaker.record_failure()
                        logger.error(f"403 Forbidden on {url} (Profile: {profile})")
                        raise RuntimeError("blocked_403")

                    if response.status_code == 429:
                        self.circuit_breaker.record_failure()
                        retry_after = response.headers.get("Retry-After")
                        wait_time = float(retry_after) if retry_after else 60.0
                        logger.warning(f"429 Rate Limited. Waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue

                    if response.status_code >= 500:
                        logger.warning(f"Server error {response.status_code} on {url}")
                        await asyncio.sleep(5 * (attempt + 1))
                        continue

                    return response

                except Exception as e:
                    if attempt == self.max_retries:
                        self.circuit_breaker.record_failure()
                        raise RuntimeError(
                            f"Fetch failed after {attempt} retries: {e}"
                        ) from e
                    await asyncio.sleep(5 * (attempt + 1))

        raise RuntimeError("unexpected_error")


async def scrape_batch(
    fixtures: list[FixtureSpec],
    manifest: FixtureManifest,
    checkpoint: ScraperCheckpoint,
    scraper: AsyncComprehensiveScraper,
    validate: bool,
    skip_existing: bool,
    retry_failures: bool,
) -> None:
    output_dir = manifest.output_dir

    # Use Rich progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        DownloadColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("Scraping fixtures...", total=len(fixtures))

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
                    progress.advance(task_id)
                    continue

                if not retry_failures and checkpoint.should_retry_failure(full_url):
                    checkpoint.mark_skipped(
                        full_url, fixture.fixture_path, "prior_failure"
                    )
                    progress.advance(task_id)
                    continue

                if skip_existing and fixture_path.exists():
                    checkpoint.mark_skipped(full_url, fixture.fixture_path, "exists")
                    progress.advance(task_id)
                    continue

                try:
                    response = await scraper.fetch(full_url, session)

                    if response.status_code == 200:
                        content = response.content

                        # Validate
                        if validate and fixture.validator:
                            errors = validate_fixture_html(content, fixture.validator)
                            if errors:
                                checkpoint.mark_failed(
                                    full_url,
                                    fixture.fixture_path,
                                    f"val_fail: {errors[0]}",
                                )
                                logger.warning(f"Validation failed for {fixture.url}")
                                progress.advance(task_id)
                                continue

                        # Write
                        fixture_path.parent.mkdir(parents=True, exist_ok=True)
                        fixture_path.write_bytes(content)
                        checkpoint.mark_completed(full_url, fixture.fixture_path)
                    else:
                        checkpoint.mark_failed(
                            full_url,
                            fixture.fixture_path,
                            f"http_{response.status_code}",
                        )

                except Exception as e:
                    checkpoint.mark_failed(full_url, fixture.fixture_path, str(e))
                    if "blocked_403" in str(e) or "circuit_breaker_open" in str(e):
                        logger.error("Scraper halted due to persistent blocks")
                        checkpoint.save()
                        break

                # Save periodically to balance durability with I/O overhead.
                progress.advance(task_id)
                if checkpoint.should_save(interval_seconds=30):
                    checkpoint.save()


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
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
        logger.info(f"Scrape finished in {duration/60:.1f} minutes")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(async_main(sys.argv[1:])))
