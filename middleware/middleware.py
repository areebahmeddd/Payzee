import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException
from pathlib import Path
from typing import Callable, Awaitable
from metrics import HTTP_REQUEST_COUNT, HTTP_REQUEST_LATENCY

# Configure logging
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

        # Log the request
        logger.info(f"Request started: {method} {path}")

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

            # Calculate and log the processing time
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
    """Middleware to limit the rate of requests."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # TODO: Implement rate limiting logic
        return await call_next(request)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # TODO: Implement authentication logic
        return await call_next(request)
