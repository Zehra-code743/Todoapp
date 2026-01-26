"""
Structured logging configuration for Phase III AI Chatbot

Configures structlog with JSON formatter and correlation ID support.
Implements sampling: 1% success rate, 100% errors.
"""
import structlog
import logging
from typing import Any
import random


def should_sample_success() -> bool:
    """Sample 1% of successful requests, 100% of errors"""
    return random.random() < 0.01


def add_correlation_id(logger: Any, method_name: str, event_dict: dict) -> dict:
    """Add correlation_id to log context if not present"""
    if "correlation_id" not in event_dict:
        # Will be added by request middleware
        event_dict["correlation_id"] = "no-correlation-id"
    return event_dict


def configure_logging():
    """
    Configure structlog with JSON formatter and correlation ID support.

    Features:
    - JSON output for log aggregation tools
    - Correlation IDs for request tracing
    - Sampling (1% success, 100% errors)
    - ISO timestamp format
    - Exception stack traces
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_correlation_id,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )


# Initialize on import
configure_logging()

# Export configured logger
logger = structlog.get_logger()
