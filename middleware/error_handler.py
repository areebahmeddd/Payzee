from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse
from starlette.exceptions import HTTPException


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors and exceptions."""

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)

            # Handle 404 response status
            if response.status_code == 404 and not request.url.path.startswith("/api"):
                html_file = Path("templates/404.html").read_text(encoding="utf-8")
                return HTMLResponse(content=html_file, status_code=404)

            return response
        except HTTPException as exc:
            # if exc.status_code == 404:
            #     return JSONResponse(status_code=404, content={"detail": "Not found"})

            # If it's a different HTTP exception, re-raise it
            raise exc
