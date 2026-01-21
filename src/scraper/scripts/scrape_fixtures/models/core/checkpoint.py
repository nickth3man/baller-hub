from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("scraper")


@dataclass
class ScraperCheckpoint:
    """Checkpoint system for resumable scraping with state persistence.

    Tracks completed, failed, and skipped fixtures to allow resuming interrupted
    scraping sessions. Automatically saves state periodically.

    Attributes:
        path: File path where checkpoint data is stored
        completed: Dictionary of successfully completed fixtures
        failed: Dictionary of failed fixtures with error details
        skipped: Dictionary of skipped fixtures with reasons
        last_save_time: Timestamp of last save operation
    """

    path: Path
    completed: dict[str, dict] = field(default_factory=dict)
    failed: dict[str, dict] = field(default_factory=dict)
    skipped: dict[str, dict] = field(default_factory=dict)
    last_save_time: float = field(default_factory=time.monotonic)

    @classmethod
    def load(cls, path: Path) -> ScraperCheckpoint:
        """Load checkpoint data from file or create new checkpoint if file doesn't exist.

        Args:
            path: Path to the checkpoint file

        Returns:
            ScraperCheckpoint instance loaded from file or newly created
        """
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
        """Save current checkpoint state to disk.

        Persists all completed, failed, and skipped fixture information
        to allow resuming interrupted scraping sessions.
        """
        payload = {
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "last_updated": datetime.now(UTC).isoformat(),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.last_save_time = time.monotonic()

    def mark_completed(self, url: str, fixture_path: str) -> None:
        """Mark a fixture as successfully completed.

        Args:
            url: The fixture URL that was successfully scraped
            fixture_path: Local path where the fixture was saved
        """
        self.completed[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.failed.pop(url, None)

    def mark_failed(self, url: str, fixture_path: str, reason: str) -> None:
        """Mark a fixture as failed with an error reason.

        Args:
            url: The fixture URL that failed
            fixture_path: Local path where the fixture should have been saved
            reason: Description of why the fixture failed
        """
        self.failed[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        }

    def mark_skipped(self, url: str, fixture_path: str, reason: str) -> None:
        """Mark a fixture as skipped with a reason.

        Args:
            url: The fixture URL that was skipped
            fixture_path: Local path where the fixture should have been saved
            reason: Reason why the fixture was skipped
        """
        self.skipped[url] = {
            "fixture_path": fixture_path,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        }

    def is_completed(self, url: str) -> bool:
        """Check if a fixture URL has been successfully completed.

        Args:
            url: The fixture URL to check

        Returns:
            True if the fixture was previously completed
        """
        return url in self.completed

    def should_retry_failure(self, url: str) -> bool:
        """Check if a previously failed fixture should be retried.

        Args:
            url: The fixture URL to check

        Returns:
            True if the fixture previously failed and can be retried
        """
        return url in self.failed

    def should_save(self, interval_seconds: float = 60.0) -> bool:
        """Check if checkpoint should be saved based on time interval.

        Args:
            interval_seconds: Minimum seconds between saves

        Returns:
            True if enough time has passed since last save
        """
        return time.monotonic() - self.last_save_time > interval_seconds
