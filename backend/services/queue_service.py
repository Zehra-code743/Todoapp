"""
Request queue with exponential backoff for OpenAI API rate limiting

Implements the queueing strategy from research.md Section 5:
- FIFO queue for maintaining request order
- Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 retries)
- Graceful degradation during rate limit events
- 30-second total timeout
"""
from asyncio import Queue, sleep
from typing import Any, Callable, TypeVar
from datetime import datetime, timedelta
from config.logging import logger
import asyncio


T = TypeVar('T')

# Global request queue
request_queue: Queue = Queue()


class RateLimitError(Exception):
    """Raised when OpenAI API rate limit is hit"""
    pass


class QueueTimeoutError(Exception):
    """Raised when request exceeds 30-second timeout"""
    pass


async def process_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 5,
    base_delay: int = 1,
    timeout_seconds: int = 30,
    **kwargs: Any
) -> T:
    """
    Execute function with exponential backoff on rate limit errors.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum retry attempts (default: 5)
        base_delay: Base delay in seconds (default: 1s)
        timeout_seconds: Total timeout in seconds (default: 30s)
        **kwargs: Keyword arguments for func

    Returns:
        Function result

    Raises:
        QueueTimeoutError: If total wait time exceeds timeout
        RateLimitError: If max retries exceeded
        Exception: Other exceptions from func

    Backoff pattern: 1s, 2s, 4s, 8s, 16s
    Total max wait: 31 seconds (within 30s timeout before last retry)
    """
    retries = 0
    start_time = datetime.utcnow()

    while retries < max_retries:
        # Check total timeout
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        if elapsed > timeout_seconds:
            logger.error("queue_timeout_exceeded",
                        retries=retries,
                        elapsed_seconds=elapsed,
                        timeout_seconds=timeout_seconds)
            raise QueueTimeoutError(f"Request timeout after {elapsed:.1f}s")

        try:
            # Attempt function call
            result = await func(*args, **kwargs)

            # Log success (with sampling in logger)
            logger.info("queue_request_success",
                       retries=retries,
                       elapsed_seconds=elapsed)

            return result

        except RateLimitError as e:
            retries += 1
            delay = base_delay * (2 ** (retries - 1))  # Exponential: 1, 2, 4, 8, 16

            logger.warning("rate_limit_hit",
                          retries=retries,
                          max_retries=max_retries,
                          delay_seconds=delay,
                          error=str(e))

            if retries >= max_retries:
                logger.error("max_retries_exceeded",
                            retries=retries,
                            elapsed_seconds=elapsed)
                raise RateLimitError(f"Max retries ({max_retries}) exceeded") from e

            # User notification after first retry
            if retries == 1:
                logger.info("user_notification",
                           message="Processing your request...",
                           reason="rate_limit")

            await sleep(delay)

        except Exception as e:
            # Non-rate-limit errors: fail immediately
            logger.error("queue_request_failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        retries=retries,
                        elapsed_seconds=elapsed)
            raise


async def enqueue_request(request: Any) -> None:
    """Add request to FIFO queue"""
    await request_queue.put(request)
    logger.info("request_enqueued",
               queue_depth=request_queue.qsize())


async def get_queue_depth() -> int:
    """Get current queue depth for monitoring"""
    return request_queue.qsize()
