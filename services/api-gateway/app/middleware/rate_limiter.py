"""
Rate limiting middleware for API Gateway
"""
from typing import Dict, Optional
import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm
    For production, use Redis-based rate limiting
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        """
        Initialize rate limiter

        Args:
            requests_per_minute: Max requests per minute per client
            requests_per_hour: Max requests per hour per client
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Store request timestamps per client
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)

        self.lock = Lock()

    def is_allowed(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed for client

        Args:
            client_id: Client identifier (IP, API key, etc.)

        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        with self.lock:
            now = time.time()

            # Clean old entries
            self._clean_old_requests(client_id, now)

            # Check minute limit
            minute_count = len(self.minute_requests[client_id])
            if minute_count >= self.requests_per_minute:
                # Calculate retry after
                oldest_request = self.minute_requests[client_id][0]
                retry_after = int(60 - (now - oldest_request)) + 1
                return False, retry_after

            # Check hour limit
            hour_count = len(self.hour_requests[client_id])
            if hour_count >= self.requests_per_hour:
                oldest_request = self.hour_requests[client_id][0]
                retry_after = int(3600 - (now - oldest_request)) + 1
                return False, retry_after

            # Record request
            self.minute_requests[client_id].append(now)
            self.hour_requests[client_id].append(now)

            return True, None

    def _clean_old_requests(self, client_id: str, now: float) -> None:
        """
        Remove old request timestamps

        Args:
            client_id: Client identifier
            now: Current timestamp
        """
        # Remove requests older than 1 minute
        minute_cutoff = now - 60
        self.minute_requests[client_id] = [
            ts for ts in self.minute_requests[client_id]
            if ts > minute_cutoff
        ]

        # Remove requests older than 1 hour
        hour_cutoff = now - 3600
        self.hour_requests[client_id] = [
            ts for ts in self.hour_requests[client_id]
            if ts > hour_cutoff
        ]

        # Clean up empty entries
        if not self.minute_requests[client_id]:
            del self.minute_requests[client_id]
        if not self.hour_requests[client_id]:
            del self.hour_requests[client_id]

    def get_usage(self, client_id: str) -> Dict[str, int]:
        """
        Get current usage for client

        Args:
            client_id: Client identifier

        Returns:
            dict: Usage statistics
        """
        with self.lock:
            now = time.time()
            self._clean_old_requests(client_id, now)

            return {
                "requests_last_minute": len(self.minute_requests[client_id]),
                "requests_last_hour": len(self.hour_requests[client_id]),
                "limit_per_minute": self.requests_per_minute,
                "limit_per_hour": self.requests_per_hour
            }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance

    Returns:
        RateLimiter: Rate limiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def reset_rate_limiter() -> None:
    """Reset global rate limiter (useful for testing)"""
    global _rate_limiter
    _rate_limiter = None
