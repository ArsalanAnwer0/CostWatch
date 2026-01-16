"""
Logging utilities for API Gateway
"""
import logging
import sys
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON

        Args:
            record: Log record to format

        Returns:
            str: JSON formatted log entry
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "duration"):
            log_data["duration_ms"] = record.duration

        return json.dumps(log_data)


def setup_logger(
    name: str,
    level: str = "INFO",
    json_format: bool = False
) -> logging.Logger:
    """
    Setup and configure logger

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting for structured logs

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Set formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Log incoming request

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        request_id: Optional request ID for tracing
        user_id: Optional user ID
    """
    extra = {}
    if request_id:
        extra["request_id"] = request_id
    if user_id:
        extra["user_id"] = user_id

    logger.info(f"{method} {path}", extra=extra)


def log_response(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: Optional[str] = None
) -> None:
    """
    Log response

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        request_id: Optional request ID for tracing
    """
    extra = {
        "duration": duration_ms
    }
    if request_id:
        extra["request_id"] = request_id

    logger.info(
        f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
        extra=extra
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log error with context

    Args:
        logger: Logger instance
        error: Exception to log
        context: Optional context information
        request_id: Optional request ID for tracing
    """
    extra = {}
    if request_id:
        extra["request_id"] = request_id

    message = f"{type(error).__name__}: {str(error)}"
    if context:
        message = f"{context} - {message}"

    logger.error(message, exc_info=True, extra=extra)
