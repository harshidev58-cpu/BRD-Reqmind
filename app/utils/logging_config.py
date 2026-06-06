"""Structured logging configuration for the BRD Generator Backend API.

This module provides JSON-formatted structured logging with request ID tracking
and security-conscious log filtering.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging.
    
    Formats log records as JSON objects with consistent structure including:
    - timestamp
    - level
    - logger name
    - message
    - request_id (if available)
    - additional context fields
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        # Exclude standard fields and internal fields
        excluded_fields = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'message', 'pathname', 'process', 'processName', 'relativeCreated',
            'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
            'request_id'
        }
        
        for key, value in record.__dict__.items():
            if key not in excluded_fields and not key.startswith('_'):
                log_data[key] = value
        
        return json.dumps(log_data)


class RequestIDFilter(logging.Filter):
    """Logging filter to add request ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to the log record if not present.
        
        Args:
            record: The log record to filter
            
        Returns:
            bool: Always True to allow the record through
        """
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        return True


class SensitiveDataFilter(logging.Filter):
    """Filter to prevent logging of sensitive data.
    
    This filter scans log messages for patterns that might indicate
    sensitive data (API keys, passwords, tokens) and redacts them.
    """
    
    SENSITIVE_PATTERNS = [
        'api_key',
        'apikey',
        'password',
        'token',
        'secret',
        'authorization',
        'bearer',
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and redact sensitive data from log records.
        
        Args:
            record: The log record to filter
            
        Returns:
            bool: Always True to allow the record through (after redaction)
        """
        # Check message for sensitive patterns
        message_lower = record.getMessage().lower()
        
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message_lower:
                # Redact the sensitive value
                record.msg = self._redact_sensitive_data(str(record.msg))
                if record.args:
                    record.args = tuple(
                        self._redact_sensitive_data(str(arg)) if isinstance(arg, str) else arg
                        for arg in record.args
                    )
        
        return True
    
    def _redact_sensitive_data(self, text: str) -> str:
        """Redact sensitive data from text.
        
        Args:
            text: Text that may contain sensitive data
            
        Returns:
            Text with sensitive data redacted
        """
        # Simple redaction: replace anything that looks like a key/token
        # This is a basic implementation - enhance as needed
        import re
        
        # Pattern for API keys (alphanumeric strings of 20+ chars)
        text = re.sub(r'\b[A-Za-z0-9_-]{20,}\b', '[REDACTED]', text)
        
        return text


def configure_structured_logging(
    level: str = "INFO",
    use_json: bool = True,
    enable_sensitive_filter: bool = True
) -> None:
    """Configure structured logging for the application.
    
    Sets up JSON-formatted logging with request ID tracking and
    sensitive data filtering.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (default: True)
        enable_sensitive_filter: Whether to enable sensitive data filtering (default: True)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Set formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    
    # Add filters
    console_handler.addFilter(RequestIDFilter())
    
    if enable_sensitive_filter:
        console_handler.addFilter(SensitiveDataFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Log configuration complete
    logging.info(
        f"Structured logging configured: level={level}, json={use_json}, "
        f"sensitive_filter={enable_sensitive_filter}"
    )


def get_logger_with_context(
    name: str,
    request_id: Optional[str] = None,
    **context
) -> logging.LoggerAdapter:
    """Get a logger with additional context.
    
    Creates a LoggerAdapter that automatically includes context fields
    in all log messages.
    
    Args:
        name: Logger name (usually __name__)
        request_id: Optional request ID to include in logs
        **context: Additional context fields to include
        
    Returns:
        LoggerAdapter with context
        
    Example:
        >>> logger = get_logger_with_context(__name__, request_id="abc123", user_id="user456")
        >>> logger.info("Processing request")
        # Logs: {"timestamp": "...", "message": "Processing request", "request_id": "abc123", "user_id": "user456"}
    """
    logger = logging.getLogger(name)
    
    extra = {}
    if request_id:
        extra['request_id'] = request_id
    extra.update(context)
    
    return logging.LoggerAdapter(logger, extra)
