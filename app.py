from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# from middleware.middleware import LoggingMiddleware, ErrorHandlerMiddleware
from routes.auth import router as auth_router
from routes.citizen import router as citizen_router
from routes.vendor import router as vendor_router
from routes.government import router as government_router
from routes.chat import router as chat_router

# Initialize FastAPI app
app = FastAPI(
    title="Payzee API",
    description="A digital payment system",
    version="1.0.0",
)

# Setup middleware
app.add_middleware(
    CORSMiddleware,  # TODO: Change CORS settings for production
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
# app.add_middleware(LoggingMiddleware)
# app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(citizen_router, prefix="/api/v1/citizens", tags=["citizen"])
app.include_router(vendor_router, prefix="/api/v1/vendors", tags=["vendor"])
app.include_router(government_router, prefix="/api/v1/governments", tags=["government"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    html_file = Path("templates/index.html").read_text()
    return html_file


@app.get("/health")
def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})
