"""
Fixture scraping module.

This module contains the logic for scraping HTML fixtures from basketball-reference.com
for use in integration testing. It includes resilience features like circuit breaking,
rate limiting, and adaptive concurrency.
"""

from __future__ import annotations

from src.scraper.scripts.scrape_fixtures.circuit_breaker import CircuitBreaker
from src.scraper.scripts.scrape_fixtures.constants import (
    DEFAULT_BASE_URL,
    DEFAULT_CHECKPOINT,
    DEFAULT_MANIFEST,
    IMPERSONATION_PROFILES,
    MIN_DISK_SPACE_GB,
)
from src.scraper.scripts.scrape_fixtures.engine import scrape_batch
from src.scraper.scripts.scrape_fixtures.models.core.checkpoint import ScraperCheckpoint
from src.scraper.scripts.scrape_fixtures.models.core.fixtures import (
    FixtureDict,
    FixtureManifest,
    FixtureSpec,
)
from src.scraper.scripts.scrape_fixtures.models.monitoring.chaos import ChaosExperiment
from src.scraper.scripts.scrape_fixtures.models.monitoring.health import HealthMetrics
from src.scraper.scripts.scrape_fixtures.scraper import AsyncComprehensiveScraper

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_CHECKPOINT",
    "DEFAULT_MANIFEST",
    "IMPERSONATION_PROFILES",
    "MIN_DISK_SPACE_GB",
    "AsyncComprehensiveScraper",
    "ChaosExperiment",
    "CircuitBreaker",
    "FixtureDict",
    "FixtureManifest",
    "FixtureSpec",
    "HealthMetrics",
    "ScraperCheckpoint",
    "scrape_batch",
]
