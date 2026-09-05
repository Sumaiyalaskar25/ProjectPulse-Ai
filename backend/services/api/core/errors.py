# services/api/core/errors.py
from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from ..middleware.request_id import get_current_request_id
from .logging import get_logger

logger = get_logger("errors")

class AppException(Exception):
    """Base application exception for domain and business errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

class ServiceUnavailableError(AppException):
    def __init__(self, message: str = "Upstream service temporarily unavailable", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles all domain/application exceptions with standardized JSON response."""
    request_id = get_current_request_id()
    logger.warning(
        f"Handled application exception [{exc.code}]: {exc.message}",
        extra={"extra_fields": {"code": exc.code, "status_code": exc.status_code, "path": request.url.path}}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id or None
            }
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches any unexpected uncaught exceptions, preventing trace leakage."""
    request_id = get_current_request_id()
    logger.error(
        f"Unhandled server error: {str(exc)}",
        exc_info=True,
        extra={"extra_fields": {"path": request.url.path, "request_id": request_id}}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please contact support if this persists.",
                "details": None,
                "request_id": request_id or None
            }
        }
    )
