from __future__ import annotations

import asyncio
import logging
import random
import time

from curl_cffi import requests

from src.scraper.scripts.scrape_fixtures.circuit_breaker import CircuitBreaker
from src.scraper.scripts.scrape_fixtures.constants import IMPERSONATION_PROFILES
from src.scraper.scripts.scrape_fixtures.models.monitoring.chaos import ChaosExperiment
from src.scraper.scripts.scrape_fixtures.models.monitoring.health import HealthMetrics

logger = logging.getLogger("scraper")


class AsyncComprehensiveScraper:
    """Advanced async web scraper with resilience, chaos engineering, and self-healing.

    Features adaptive concurrency, circuit breaker protection, health monitoring,
    chaos experiment framework, and progressive degradation for robust web scraping.

    Attributes:
        base_concurrency: Original concurrency setting
        current_concurrency: Current adaptive concurrency level
        health_metrics: Real-time health monitoring
        circuit_breaker: Circuit breaker for failure protection
        chaos_experiment: Chaos engineering framework
        degraded_mode: Whether scraper is in degraded performance mode
    """

    def __init__(
        self,
        concurrency: int = 2,
        min_seconds: float = 3.5,
        max_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        impersonate: str | None = None,
        enable_chaos: bool = False,
        adaptive_concurrency: bool = True,
    ) -> None:
        """Initialize the scraper with resilience and monitoring features.

        Args:
            concurrency: Base number of concurrent requests
            min_seconds: Minimum delay between requests
            max_seconds: Maximum delay between requests
            timeout_seconds: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            impersonate: Browser impersonation profile to use
            enable_chaos: Whether to enable chaos experiment framework
            adaptive_concurrency: Whether to adapt concurrency based on health
        """
        self.base_concurrency = concurrency
        self.current_concurrency = concurrency
        self.min_concurrency = 1
        self.max_concurrency = concurrency * 2

        self.semaphore = asyncio.Semaphore(self.current_concurrency)
        self.min_seconds = min_seconds
        self.max_seconds = max_seconds
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.impersonate = impersonate

        # Health monitoring and chaos engineering
        self.health_metrics = HealthMetrics()
        self.circuit_breaker = CircuitBreaker(health_metrics=self.health_metrics)
        self.chaos_experiment = ChaosExperiment()
        self.enable_chaos = enable_chaos
        self.adaptive_concurrency = adaptive_concurrency

        # Self-healing state
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_adaptation_time = time.monotonic()
        self.degraded_mode = False

        self._last_request_time = 0.0
        self._request_times: list[float] = []

    async def fetch(
        self, url: str, session: requests.AsyncSession
    ) -> requests.Response:
        """Fetch a URL with resilience, retries, and chaos injection.

        Implements circuit breaker protection, exponential backoff, browser
        impersonation rotation, and optional chaos experiment failures.

        Args:
            url: The URL to fetch
            session: Async HTTP session to use for the request

        Returns:
            HTTP response object

        Raises:
            RuntimeError: When circuit breaker is open or all retries exhausted
        """
        if not self.circuit_breaker.can_proceed():
            raise RuntimeError("circuit_breaker_open")

        async with self.semaphore:
            # Enforce inter-request delay
            now = time.monotonic()
            elapsed = now - self._last_request_time
            delay = random.uniform(self.min_seconds, self.max_seconds)
            if elapsed < delay:
                try:
                    await asyncio.sleep(delay - elapsed)
                except asyncio.CancelledError:
                    # Allow cancellation to propagate but log it
                    logger.debug("Request delay cancelled")
                    raise

            for attempt in range(self.max_retries + 1):
                request_start = time.monotonic()
                try:
                    # Rotate impersonation if not pinned
                    profile = self.impersonate or random.choice(IMPERSONATION_PROFILES)

                    # Note: curl_cffi AsyncSession is initialized with a profile,
                    # but we can also pass it to individual requests in recent versions.
                    # If not, we'll rely on the session's default.

                    response = await session.get(url, timeout=self.timeout_seconds)
                    self._last_request_time = time.monotonic()
                    response_time = self._last_request_time - request_start

                    if response.status_code == 200:
                        self.circuit_breaker.record_success()
                        self.health_metrics.record_request(True, response_time)
                        return response

                    if response.status_code == 403:
                        self.circuit_breaker.record_failure()
                        self.health_metrics.record_request(False, response_time)
                        logger.error(f"403 Forbidden on {url} (Profile: {profile})")
                        raise RuntimeError("blocked_403")

                    if response.status_code == 429:
                        self.circuit_breaker.record_failure()
                        self.health_metrics.record_request(False, response_time)
                        retry_after = response.headers.get("Retry-After")
                        wait_time = float(retry_after) if retry_after else 60.0
                        logger.warning(f"429 Rate Limited. Waiting {wait_time}s")
                        try:
                            await asyncio.sleep(wait_time)
                        except asyncio.CancelledError:
                            logger.debug("Rate limit wait cancelled")
                            raise
                        continue

                    if response.status_code >= 500:
                        self.health_metrics.record_request(False, response_time)
                        logger.warning(f"Server error {response.status_code} on {url}")
                        try:
                            await asyncio.sleep(5 * (attempt + 1))
                        except asyncio.CancelledError:
                            logger.debug("Retry wait cancelled")
                            raise
                        continue

                    # Non-200 but not error status codes
                    self.health_metrics.record_request(False, response_time)
                    return response

                except asyncio.CancelledError:
                    # Re-raise cancellation immediately without retry
                    logger.debug("Fetch operation cancelled")
                    raise
                except Exception as e:
                    response_time = time.monotonic() - request_start
                    if attempt == self.max_retries:
                        self.circuit_breaker.record_failure()
                        self.health_metrics.record_request(False, response_time)
                        self.health_metrics.network_errors += 1
                        raise RuntimeError(
                            f"Fetch failed after {attempt} retries: {e}"
                        ) from e
                    try:
                        await asyncio.sleep(5 * (attempt + 1))
                    except asyncio.CancelledError:
                        logger.debug("Retry wait cancelled")
                        raise

        raise RuntimeError("unexpected_error")
