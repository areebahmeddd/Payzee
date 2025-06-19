import time
import logging
import threading
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from monitoring.metrics import RATE_LIMIT_EXCEEDED

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit the number of requests from a single IP address."""

    def __init__(self, app, request_limit=50, cooldown_seconds=60):
        """
        Initialize the rate limiter with default settings:
        - request_limit: Maximum number of requests allowed in the cooldown period.
        - cooldown_seconds: Time period in seconds for the rate limit.
        """
        super().__init__(app)
        self.request_limit = request_limit
        self.cooldown_seconds = cooldown_seconds
        self.request_records = {}  # IP -> list of request timestamps
        self.lock = threading.Lock()  # For thread safety

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        with self.lock:
            # Initialize if first request from this IP
            if client_ip not in self.request_records:
                self.request_records[client_ip] = []

            # Remove timestamps older than the cooldown period
            window_start = current_time - self.cooldown_seconds
            self.request_records[client_ip] = [
                timestamp
                for timestamp in self.request_records[client_ip]
                if timestamp > window_start
            ]

            # Count requests in the current window
            current_count = len(self.request_records[client_ip])
            if current_count >= self.request_limit:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                RATE_LIMIT_EXCEEDED.labels(client_ip=client_ip).inc()

                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please try again after 60 seconds.",
                    },
                )

            # Add current request to the record
            self.request_records[client_ip].append(current_time)

        # Continue processing the request if under rate limit
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract the client IP address from the request."""
        # Check forwarded headers (for clients behind proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Fall back to the client's direct IP
        client_host = request.client.host if request.client else "unknown"
        return client_host
