# services/api/core/logging.py
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional
from ..middleware.request_id import get_current_request_id

class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON including timestamp and request_id."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_current_request_id() or None,
        }
        
        # Include extra fields if attached
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_entry.update(record.extra_fields)
            
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def get_logger(name: str = "projectpulse") -> logging.Logger:
    """Retrieve a configured structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger
