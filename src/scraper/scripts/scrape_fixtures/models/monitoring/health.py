from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class HealthMetrics:
    """Real-time health monitoring for the scraper."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_breaker_trips: int = 0
    average_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_percent: float = 0.0
    network_errors: int = 0
    validation_errors: int = 0
    last_health_check: float = field(default_factory=time.monotonic)
    failure_rate_window: list[bool] = field(default_factory=lambda: [])

    def record_request(self, success: bool, response_time: float = 0.0) -> None:
        """Record a request result and update metrics.

        Args:
            success: Whether the request was successful
            response_time: Time taken for the request in seconds
        """
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        # Update rolling average response time
        if response_time > 0:
            self.average_response_time = (
                self.average_response_time * (self.total_requests - 1) + response_time
            ) / self.total_requests

        # Maintain failure rate window (last 100 requests)
        self.failure_rate_window.append(not success)
        if len(self.failure_rate_window) > 100:
            self.failure_rate_window.pop(0)

    def get_failure_rate(self) -> float:
        """Get failure rate over the recent window.

        Returns:
            Failure rate as a float between 0.0 and 1.0
        """
        if not self.failure_rate_window:
            return 0.0
        return sum(self.failure_rate_window) / len(self.failure_rate_window)

    def get_health_score(self) -> float:
        """Calculate overall health score (0-100, higher is better).

        Returns:
            Health score between 0 and 100, where higher scores indicate better health
        """
        if self.total_requests == 0:
            return 100.0

        success_rate = self.successful_requests / self.total_requests
        failure_rate = self.get_failure_rate()

        # Penalize high failure rates and circuit breaker trips
        penalty = min(50, self.circuit_breaker_trips * 5 + failure_rate * 20)

        return max(0, (success_rate * 100) - penalty)

    def should_trigger_degradation(self) -> bool:
        """Check if conditions warrant progressive degradation.

        Returns:
            True if progressive degradation should be triggered
        """
        failure_rate = self.get_failure_rate()
        return (
            failure_rate > 0.3
            or self.circuit_breaker_trips > 2  # >30% failure rate
            or self.memory_usage_mb > 500  # Multiple circuit breaker trips
            or self.disk_usage_percent > 90  # High memory usage
        )  # Low disk space
