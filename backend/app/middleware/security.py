# app/middleware/security.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import time
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Relax CSP for API docs in development mode
        if settings.DEBUG and request.url.path in [
            "/api/docs",
            "/api/redoc",
            "/openapi.json",
        ]:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        else:
            # Strict CSP for production/other endpoints
            response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Add request ID and timing
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = (
            request.state.request_id if hasattr(request.state, "request_id") else ""
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED or not self.redis:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}:{request.url.path}"

        try:
            # Check rate limit
            current = await self.redis.incr(key)

            if current == 1:
                await self.redis.expire(key, settings.RATE_LIMIT_PERIOD)

            if current > settings.RATE_LIMIT_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"},
                    headers={
                        "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(
                            time.time() + settings.RATE_LIMIT_PERIOD
                        ),
                    },
                )

            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
            response.headers["X-RateLimit-Remaining"] = str(
                settings.RATE_LIMIT_REQUESTS - current
            )

            return response

        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            return await call_next(request)
