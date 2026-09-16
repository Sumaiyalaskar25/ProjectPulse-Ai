# services/api/middleware/rate_limit.py
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from ..core.errors import AppException
from ..core.logging import get_logger

logger = get_logger("rate_limit")

class RateLimitExceeded(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Please retry shortly."):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

class InMemoryRateLimiter:
    """
    Sliding window per-key rate limiter.
    Stores list of request timestamps per key (e.g. client IP or user ID).
    """
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds
        
        # Clean older records
        valid_requests = [ts for ts in self._requests[key] if ts > window_start]
        self._requests[key] = valid_requests
        
        if len(valid_requests) >= max_requests:
            retry_after = int(valid_requests[0] - window_start) + 1
            return False, max(1, retry_after)
        
        self._requests[key].append(now)
        return True, 0

_limiter = InMemoryRateLimiter()

def rate_limit(max_requests: int = 30, window_seconds: int = 60):
    """
    FastAPI dependency factory for endpoint rate limiting.
    """
    async def dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"{client_ip}:{request.url.path}"
        
        allowed, retry_after = _limiter.is_allowed(key, max_requests, window_seconds)
        if not allowed:
            logger.warning(f"Rate limit hit for key={key}, retry_after={retry_after}s")
            raise RateLimitExceeded(
                message=f"Too many requests. Rate limit is {max_requests} req / {window_seconds}s. Please retry in {retry_after} seconds."
            )
    return dependency
