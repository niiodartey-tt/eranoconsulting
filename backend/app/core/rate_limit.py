# app/core/rate_limit.py
"""Simple rate limiting decorator"""
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)


def rate_limit(requests: int = 100, period: int = 60):
    """
    Rate limiting decorator
    
    Args:
        requests: Number of requests allowed
        period: Time period in seconds
    
    Note: This is a placeholder decorator for development.
    For production, use Redis-based rate limiting or a library like slowapi.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # In development, just pass through
            # TODO: Implement Redis-based rate limiting for production
            logger.debug(f"Rate limit check: {requests} requests per {period} seconds")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
