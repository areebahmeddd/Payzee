import time
import logging
import threading
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException
from typing import Callable, Awaitable
from metrics import (
    HTTP_REQUEST_COUNT,
    HTTP_REQUEST_LATENCY,
    RATE_LIMIT_EXCEEDED,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests, responses, and tracking metrics."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        method = request.method
        path = request.url.path

        try:
            # Process the request
            response = await call_next(request)

            # Record metrics
            status_code = response.status_code
            duration = time.time() - start_time

            HTTP_REQUEST_COUNT.labels(
                method=method, endpoint=path, http_status=status_code
            ).inc()
            HTTP_REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)

            # Log the request and response
            logger.info(
                f"Request completed: {method} {path} - Status: {status_code} - Time: {duration:.3f}s"
            )

            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error processing request: {method} {path} - Error: {str(e)}")
            HTTP_REQUEST_COUNT.labels(
                method=method, endpoint=path, http_status=500
            ).inc()
            HTTP_REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors and exceptions."""

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)

            # Handle 404 response status
            if response.status_code == 404:
                html_file = Path("templates/404.html").read_text()
                return HTMLResponse(content=html_file, status_code=404)

            return response
        except HTTPException as exc:
            if exc.status_code == 404:
                return JSONResponse(status_code=404, content={"detail": "Not found"})

            # If it's a different HTTP exception, re-raise it
            raise exc


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit the number of requests from a single IP address."""

    def __init__(self, app, request_limit=30, cooldown_seconds=60):
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


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # TODO: Implement JWT or Auth0
        return await call_next(request)
