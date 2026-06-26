import time
from collections import defaultdict
from threading import Lock
from typing import Tuple

# Configurable limits
MAX_REQUESTS_PER_WINDOW = int(__import__("os").getenv("RATE_LIMIT_REQUESTS", "20"))
WINDOW_SECONDS = int(__import__("os").getenv("RATE_LIMIT_WINDOW", "60"))


class _RateLimiter:
    def __init__(self):
        self._lock = Lock()
        # ip -> (window_start, count)
        self._windows: dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    def is_allowed(self, ip: str) -> Tuple[bool, int]:
        """Returns (allowed, retry_after_seconds). retry_after_seconds is 0 when allowed."""
        now = time.time()
        with self._lock:
            window_start, count = self._windows[ip]
            if now - window_start >= WINDOW_SECONDS:
                self._windows[ip] = (now, 1)
                return True, 0
            if count < MAX_REQUESTS_PER_WINDOW:
                self._windows[ip] = (window_start, count + 1)
                return True, 0
            retry_after = int(WINDOW_SECONDS - (now - window_start)) + 1
            return False, retry_after

    def _cleanup(self):
        """Remove stale entries to prevent unbounded memory growth."""
        now = time.time()
        with self._lock:
            stale = [ip for ip, (ws, _) in self._windows.items() if now - ws >= WINDOW_SECONDS * 2]
            for ip in stale:
                del self._windows[ip]


limiter = _RateLimiter()
