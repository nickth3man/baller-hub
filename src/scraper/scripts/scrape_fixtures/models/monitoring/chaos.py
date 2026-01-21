from __future__ import annotations

import logging
import random
import socket
import ssl
import time
from dataclasses import dataclass, field

logger = logging.getLogger("scraper")


@dataclass
class ChaosExperiment:
    """Framework for controlled chaos experiments."""

    enabled: bool = False
    experiment_name: str = ""
    failure_types: dict[str, bool] = field(default_factory=dict)
    injection_probability: float = 0.0
    active_duration: float = 0.0
    start_time: float = 0.0

    def start_experiment(
        self,
        name: str,
        failure_types: dict[str, bool],
        probability: float = 0.1,
        duration_minutes: float = 5.0,
    ) -> None:
        """Start a chaos experiment."""
        self.enabled = True
        self.experiment_name = name
        self.failure_types = failure_types
        self.injection_probability = probability
        self.active_duration = duration_minutes * 60
        self.start_time = time.monotonic()
        logger.warning(
            f"CHAOS EXPERIMENT STARTED: {name} ({probability * 100:.1f}% injection for {duration_minutes}m)"
        )

    def should_inject_failure(self, failure_type: str) -> bool:
        """Check if a failure should be injected."""
        if not self.enabled:
            return False

        # Check if experiment has expired
        if time.monotonic() - self.start_time > self.active_duration:
            self.enabled = False
            logger.info(f"CHAOS EXPERIMENT ENDED: {self.experiment_name}")
            return False

        return (
            self.failure_types.get(failure_type, False)
            and random.random() < self.injection_probability
        )

    def inject_network_failure(self, failure_type: str) -> None:
        """Inject network-related failures."""
        if failure_type == "timeout":
            raise TimeoutError("Chaos: Network timeout injected")
        elif failure_type == "connection_error":
            raise ConnectionError("Chaos: Connection failed")
        elif failure_type == "dns_error":
            raise socket.gaierror("Chaos: DNS resolution failed")
        elif failure_type == "tls_error":
            raise ssl.SSLError("Chaos: TLS handshake failed")

    def inject_resource_failure(self, failure_type: str) -> None:
        """Inject resource-related failures."""
        if failure_type == "disk_full":
            raise OSError("Chaos: No space left on device")
        elif failure_type == "memory_error":
            raise MemoryError("Chaos: Out of memory")
        elif failure_type == "permission_error":
            raise PermissionError("Chaos: Permission denied")

    def inject_validation_failure(self) -> list[str]:
        """Inject validation failures."""
        return ["Chaos: Validation failure injected"]
