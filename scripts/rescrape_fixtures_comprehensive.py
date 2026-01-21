"""Rescrape basketball-reference fixtures with checkpoints and validation."""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from src.utils.fixture_validation import validate_fixture_html

DEFAULT_BASE_URL = "https://www.basketball-reference.com"
DEFAULT_MANIFEST = Path("scripts/fixture_manifest.json")
DEFAULT_CHECKPOINT = Path("scraper_checkpoint.json")


@dataclass(frozen=True)
class FixtureSpec:
    url: str
    fixture_path: str
    validator: str | None = None


@dataclass(frozen=True)
class FixtureManifest:
    base_url: str
    output_dir: Path
    fixtures: list[FixtureSpec]

    @classmethod
    def load(cls, path: Path) -> FixtureManifest:
        data = json.loads(path.read_text(encoding="utf-8"))
        base_url = data.get("base_url", DEFAULT_BASE_URL)
        output_dir = Path(data.get("output_dir", "tests/integration/files"))
        fixtures = [
            FixtureSpec(
                url=fixture["url"],
                fixture_path=fixture["fixture_path"],
                validator=fixture.get("validator"),
            )
            for fixture in data.get("fixtures", [])
        ]
        return cls(base_url=base_url, output_dir=output_dir, fixtures=fixtures)


@dataclass
class ScraperCheckpoint:
    path: Path
    completed: dict[str, dict] = field(default_factory=dict)
    failed: dict[str, dict] = field(default_factory=dict)
    skipped: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> ScraperCheckpoint:
        if not path.exists():
            return cls(path=path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            path=path,
            completed=data.get("completed", {}),
            failed=data.get("failed", {}),
            skipped=data.get("skipped", {}),
        )

    def save(self) -> None:
        payload = {
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def mark_completed(self, url: str, fixture_path: str) -> None:
        self.completed[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
        }

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


@dataclass
class ScraperMetrics:
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    errors_by_type: dict[str, int] = field(default_factory=dict)

    def record_error(self, error_type: str) -> None:
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1


class JitterRateLimiter:
    """Rate limiter with randomized delay per request."""

    def __init__(self, min_seconds: float = 3.5, max_seconds: float = 5.0) -> None:
        self._min_seconds = min_seconds
        self._max_seconds = max_seconds
        self._last_request = 0.0

    def wait(self) -> None:
        target_interval = random.uniform(self._min_seconds, self._max_seconds)
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < target_interval:
            time.sleep(target_interval - elapsed)
        self._last_request = time.monotonic()


class ComprehensiveScraper:
    """Scrape fixtures with retry, checkpointing, and validation."""

    def __init__(
        self,
        min_seconds: float = 3.5,
        max_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        retry_backoff_base: float = 5.0,
        stop_on_403: bool = True,
    ) -> None:
        self.rate_limiter = JitterRateLimiter(
            min_seconds=min_seconds, max_seconds=max_seconds
        )
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base
        self.stop_on_403 = stop_on_403
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )
        return session

    def fetch(self, url: str) -> requests.Response:
        for attempt in range(self.max_retries + 1):
            self.rate_limiter.wait()
            try:
                response = self.session.get(url, timeout=self.timeout_seconds)
            except requests.RequestException as exc:
                if attempt == self.max_retries:
                    raise RuntimeError(f"network_error: {exc}") from exc
                self._sleep_backoff(attempt)
                continue

            if response.status_code == 403:
                if self.stop_on_403:
                    raise RuntimeError("blocked_403")
                return response

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    with _suppress_value_error():
                        time.sleep(float(retry_after))
                        continue
                self._sleep_backoff(attempt)
                continue

            if response.status_code >= 500:
                if attempt == self.max_retries:
                    return response
                self._sleep_backoff(attempt)
                continue

            return response

        raise RuntimeError("unexpected_retry_exhaustion")

    def _sleep_backoff(self, attempt: int) -> None:
        delay = min(300.0, self.retry_backoff_base * (2**attempt))
        time.sleep(delay)


def scrape_fixtures(
    manifest: FixtureManifest,
    checkpoint: ScraperCheckpoint,
    scraper: ComprehensiveScraper,
    validate: bool,
    skip_existing: bool,
    retry_failures: bool,
) -> ScraperMetrics:
    metrics = ScraperMetrics(total=len(manifest.fixtures))
    output_dir = manifest.output_dir

    for fixture in manifest.fixtures:
        full_url = _build_url(manifest.base_url, fixture.url)
        fixture_path = output_dir / fixture.fixture_path

        if checkpoint.is_completed(full_url):
            metrics.skipped += 1
            checkpoint.mark_skipped(full_url, fixture.fixture_path, "checkpointed")
            continue

        if not retry_failures and checkpoint.should_retry_failure(full_url):
            metrics.skipped += 1
            checkpoint.mark_skipped(full_url, fixture.fixture_path, "prior_failure")
            continue

        if skip_existing and fixture_path.exists():
            metrics.skipped += 1
            checkpoint.mark_skipped(full_url, fixture.fixture_path, "fixture_exists")
            continue

        try:
            response = scraper.fetch(full_url)
        except RuntimeError as exc:
            reason = str(exc)
            metrics.failed += 1
            metrics.record_error(reason)
            checkpoint.mark_failed(full_url, fixture.fixture_path, reason)
            if reason == "blocked_403":
                checkpoint.save()
                raise
            continue

        if response.status_code == 404:
            metrics.failed += 1
            metrics.record_error("not_found_404")
            checkpoint.mark_failed(full_url, fixture.fixture_path, "not_found_404")
            continue

        if response.status_code != 200:
            metrics.failed += 1
            metrics.record_error(f"http_{response.status_code}")
            checkpoint.mark_failed(
                full_url, fixture.fixture_path, f"http_{response.status_code}"
            )
            continue

        content = response.content
        if validate and fixture.validator:
            errors = validate_fixture_html(content, fixture.validator)
            if errors:
                unvalidated_path = fixture_path.with_suffix(
                    f"{fixture_path.suffix}.unvalidated"
                )
                _write_fixture(unvalidated_path, content)
                metrics.failed += 1
                metrics.record_error("validation_failed")
                checkpoint.mark_failed(
                    full_url,
                    fixture.fixture_path,
                    "validation_failed: " + "; ".join(errors),
                )
                continue

        _write_fixture(fixture_path, content)
        metrics.completed += 1
        checkpoint.mark_completed(full_url, fixture.fixture_path)

        if (metrics.completed + metrics.failed + metrics.skipped) % 10 == 0:
            checkpoint.save()

    checkpoint.save()
    return metrics


def _build_url(base_url: str, url: str) -> str:
    if url.startswith("http"):
        return url
    return urljoin(base_url, url)


def _write_fixture(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


class _suppress_value_error:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc, exc_tb) -> bool:
        return exc_type is ValueError


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to fixture manifest JSON.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=DEFAULT_CHECKPOINT,
        help="Path to checkpoint JSON.",
    )
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--min-seconds", type=float, default=3.5)
    parser.add_argument("--max-seconds", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--retry-backoff-base", type=float, default=5.0)
    parser.add_argument("--continue-on-403", action="store_true")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    manifest = FixtureManifest.load(args.manifest)
    checkpoint = ScraperCheckpoint.load(args.checkpoint)
    scraper = ComprehensiveScraper(
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        retry_backoff_base=args.retry_backoff_base,
        stop_on_403=not args.continue_on_403,
    )

    try:
        metrics = scrape_fixtures(
            manifest=manifest,
            checkpoint=checkpoint,
            scraper=scraper,
            validate=not args.no_validate,
            skip_existing=not args.no_skip_existing,
            retry_failures=args.retry_failures,
        )
    except RuntimeError as exc:
        print(f"Scraper halted: {exc}", file=sys.stderr)
        return 2

    print(
        "Scrape complete:",
        f"total={metrics.total}",
        f"completed={metrics.completed}",
        f"failed={metrics.failed}",
        f"skipped={metrics.skipped}",
        f"errors={metrics.errors_by_type}",
    )
    return 0 if metrics.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
