from __future__ import annotations

import logging
import time

from src.scraper.scripts.scrape_fixtures.models.monitoring.health import HealthMetrics

logger = logging.getLogger("scraper")


class CircuitBreaker:
    """Enhanced circuit breaker with health monitoring and half-open state.

    Implements the circuit breaker pattern to prevent cascading failures by
    temporarily stopping requests when failure rates are high. Includes
    half-open state for gradual recovery testing.

    Attributes:
        failure_threshold: Number of failures before opening the circuit
        reset_timeout: Seconds to wait before attempting to close circuit
        health_metrics: Optional health metrics tracker
        trip_count: Total number of times circuit has opened
        half_open_success_count: Successes during half-open testing
        half_open_failure_count: Failures during half-open testing
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout_seconds: float = 300.0,
        health_metrics: HealthMetrics | None = None,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout_seconds
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"
        self.health_metrics = health_metrics
        self.trip_count = 0
        self.half_open_success_count = 0
        self.half_open_failure_count = 0

    def record_failure(self) -> None:
        """Record a request failure and potentially open the circuit.

        Updates failure counts and transitions circuit state based on
        failure threshold and current state.
        """
        self.failure_count += 1
        self.last_failure_time = time.monotonic()

        if self.state == "HALF_OPEN":
            self.half_open_failure_count += 1
            # If we fail in half-open state, go back to open
            self.state = "OPEN"
            logger.warning("Circuit breaker returned to OPEN (half-open failure)")

        elif self.failure_count >= self.failure_threshold and self.state == "CLOSED":
            self.state = "OPEN"
            self.trip_count += 1
            if self.health_metrics:
                self.health_metrics.circuit_breaker_trips += 1
            logger.warning(
                f"Circuit breaker OPENED after {self.failure_count} failures (trip #{self.trip_count})"
            )

    def record_success(self) -> None:
        """Record a successful request and potentially close or stabilize the circuit.

        Resets failure counts and transitions from half-open to closed state
        after sufficient successes.
        """
        if self.state == "HALF_OPEN":
            self.half_open_success_count += 1
            # Require multiple successes in half-open before closing
            if self.half_open_success_count >= 3:
                self.failure_count = 0
                self.state = "CLOSED"
                self.half_open_success_count = 0
                self.half_open_failure_count = 0
                logger.info("Circuit breaker CLOSED (half-open successes)")
        elif self.state == "CLOSED":
            self.failure_count = max(0, self.failure_count - 1)  # Gradual recovery

    def can_proceed(self) -> bool:
        """Check if requests can proceed based on circuit state.

        Returns:
            True if circuit is closed or in half-open state, False if open
        """
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if (
                self.last_failure_time
                and time.monotonic() - self.last_failure_time > self.reset_timeout
            ):
                self.state = "HALF_OPEN"
                self.half_open_success_count = 0
                self.half_open_failure_count = 0
                logger.info("Circuit breaker testing HALF_OPEN state")
                return True
            return False
        return True  # HALF_OPEN allows requests

    def get_health_status(self) -> dict:
        """Get detailed circuit breaker health status.

        Returns:
            Dictionary containing circuit breaker state and statistics
        """
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "trip_count": self.trip_count,
            "half_open_successes": self.half_open_success_count,
            "half_open_failures": self.half_open_failure_count,
            "time_since_last_failure": (
                time.monotonic() - self.last_failure_time
                if self.last_failure_time
                else None
            ),
        }
