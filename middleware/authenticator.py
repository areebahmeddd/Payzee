from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette import status
from utils.auth import verify_token


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle JWT-based authentication."""

    # Routes that don't require authentication
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/templates/favicon.ico",
        "/api/v1/auth/signup/citizen",
        "/api/v1/auth/signup/vendor",
        "/api/v1/auth/signup/government",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/chat/",
    }

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip authentication for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Only apply authentication to API routes
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)

        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
            )

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
            )

        try:
            token_data = verify_token(token)
            request.state.user_id = token_data["user_id"]
            request.state.user_type = token_data["user_type"]
            request.state.token_exp = token_data["exp"]
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(e)}
            )

        return await call_next(request)
