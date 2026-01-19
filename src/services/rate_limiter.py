"""Rate limiting service."""

import time
import threading


class RateLimiter:
    """
    Thread-safe rate limiter with Retry-After support.

    Enforces a minimum interval between requests to respect
    basketball-reference.com's rate limits (approx 20 req/min).
    """

    def __init__(self, min_interval=3.5):
        """
        Initialize the rate limiter.

        Args:
            min_interval (float): Minimum seconds between requests.
                                  Defaults to 3.5s (conservative).
        """
        self._min_interval = min_interval
        self._last_request = 0.0
        self._lock = threading.Lock()

    def wait(self):
        """
        Block until the rate limit allows the next request.
        """
        with self._lock:
            current_time = time.monotonic()
            elapsed = current_time - self._last_request

            if elapsed < self._min_interval:
                sleep_time = self._min_interval - elapsed
                time.sleep(sleep_time)

            self._last_request = time.monotonic()

    def update_from_response(self, response):
        """
        Update the rate limit based on the Retry-After header.

        Args:
            response (requests.Response): The HTTP response.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                # Retry-After can be seconds (int) or HTTP date
                # We assume seconds for simplicity as that's common for 429s
                delay = float(retry_after)
                with self._lock:
                    # Temporarily increase interval if needed, or just sleep now?
                    # Ideally, we just ensure the NEXT request waits at least this long.
                    # Setting last_request so that (now - last) < interval is tricky.
                    # Instead, we'll just force a sleep if we are in a tight loop,
                    # but typically this is handled by the Retry adapter catching 429s.
                    # However, to be good citizens, if we see this header on a 200 OK (unlikely)
                    # or error, we should respect it.

                    # For simple strict rate limiting, we can just ensure min_interval
                    # captures this pressure.
                    self._min_interval = max(self._min_interval, delay)
            except (ValueError, TypeError):
                pass
