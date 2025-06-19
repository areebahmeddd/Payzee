from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # TODO: Implement JWT or Auth0
        return await call_next(request)
