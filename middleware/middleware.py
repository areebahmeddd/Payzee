import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Awaitable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        # Log the request
        logger.info(f"Request started: {request.method} {request.url.path}")

        # Process the request
        response = await call_next(request)

        # Calculate and log the processing time
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        return response


# class ErrorHandlerMiddleware(BaseHTTPMiddleware):
#     """Middleware to handle errors and exceptions."""

#     async def dispatch(self, request, call_next):
#         try:
#             response = await call_next(request)

#             # Handle 404 response status
#             if response.status_code == 404:
#                 html_file = Path("templates/404.html").read_text()
#                 return HTMLResponse(content=html_file, status_code=404)

#             return response
#         except StarletteHTTPException as exc:
#             if exc.status_code == 404:
#                 return JSONResponse(status_code=404, content={"detail": "Not found"})

#             # If it's a different HTTP exception, re-raise it
#             raise exc


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
