# services/api/middleware/request_id.py
import uuid
import time
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable for holding the current request ID across async tasks
REQUEST_ID_CTX: ContextVar[str] = ContextVar("request_id", default="")

def get_current_request_id() -> str:
    """Retrieve the current request ID from context."""
    return REQUEST_ID_CTX.get()

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every incoming request has a unique correlation ID (X-Request-ID)
    and attaches execution duration header (X-Process-Time-Ms).
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract or generate unique request ID
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        token = REQUEST_ID_CTX.set(request_id)
        
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            REQUEST_ID_CTX.reset(token)
            
        process_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Attach tracing headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
        
        return response
