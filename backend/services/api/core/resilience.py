# services/api/core/resilience.py
import time
import inspect
import logging
from functools import wraps
from typing import Callable, Any, Type, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from .logging import get_logger
from .errors import ServiceUnavailableError

logger = get_logger("resilience")

def with_retry(
    max_attempts: int = 3,
    min_wait: float = 0.5,
    max_wait: float = 4.0,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying async operations with exponential backoff.
    Ideal for LLM API calls, external scrapers, and network I/O.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(retry_exceptions),
        reraise=True,
        before_sleep=before_sleep_log(logger, log_level=logging.WARNING)
    )

class SimpleCircuitBreaker:
    """
    Lightweight asynchronous Circuit Breaker to prevent cascading failures.
    States: CLOSED (normal), OPEN (tripped/failing), HALF_OPEN (probing).
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()
        
        if self.state == "OPEN":
            if now - self.last_failure_time > self.recovery_timeout_sec:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN (probing service)")
            else:
                raise ServiceUnavailableError(
                    message="Service circuit is open due to repeated upstream failures. Please try again shortly."
                )

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Reset on success
            if self.state in ("HALF_OPEN", "OPEN"):
                logger.info("Circuit breaker recovered: transitioning to CLOSED")
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception as exc:
            self.failure_count += 1
            self.last_failure_time = now
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"Circuit breaker tripped to OPEN state after {self.failure_count} consecutive failures: {exc}"
                )
            raise
