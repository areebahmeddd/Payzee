import time
import logging
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from monitoring.metrics import (
    HTTP_REQUEST_COUNT,
    HTTP_REQUEST_LATENCY,
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
