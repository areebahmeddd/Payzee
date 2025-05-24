# import os
# import sentry_sdk
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# from sentry_sdk.integrations.fastapi import FastApiIntegration
# from sentry_sdk.integrations.redis import RedisIntegration
from starlette_exporter import PrometheusMiddleware, handle_metrics
from middleware.middleware import (
    LoggingMiddleware,
    ErrorHandlerMiddleware,
    RateLimitMiddleware,
)
from db.redis_config import redis_client
from routes.auth import router as auth_router
from routes.citizen import router as citizen_router
from routes.vendor import router as vendor_router
from routes.government import router as government_router
from routes.chat import router as chat_router

# Initialize Sentry (Used in prod environment)
# sentry_sdk.init(
#     dsn=os.environ.get("SENTRY_DSN"),
#     environment=os.environ.get("SENTRY_ENV"),
#     integrations=[
#         FastApiIntegration(),
#         RedisIntegration(),
#     ],
# )

# Initialize FastAPI app
app = FastAPI(
    title="Payzee API",
    description="A digital payment system",
    version="1.0.0",
)

# Setup middleware (* for dev environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware)

# Add Prometheus middleware for metrics
app.add_middleware(
    PrometheusMiddleware,
    app_name="payzee",
    group_paths=True,
    filter_unhandled_paths=False,
    prefix="payzee",
)
app.add_route("/metrics", handle_metrics)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(citizen_router, prefix="/api/v1/citizens", tags=["citizen"])
app.include_router(vendor_router, prefix="/api/v1/vendors", tags=["vendor"])
app.include_router(government_router, prefix="/api/v1/governments", tags=["government"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chatbot"])


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    html_file = Path("templates/index.html").read_text()
    return html_file


@app.get("/health")
def health_check() -> JSONResponse:
    api_start_time = time.time()
    api_status = {
        "name": "FastAPI",
        "title": "API Check",
        "code": 200,
        "message": "All OK",
        "latency": 0,
    }
    api_latency = time.time() - api_start_time
    api_status["latency"] = round(api_latency, 4)

    db_start_time = time.time()
    db_status = {
        "name": "Redis Database",
        "title": "Database Check",
        "code": 200,
        "message": "All OK",
        "latency": 0,
    }

    try:
        redis_client.ping()
    except Exception as e:
        db_status["code"] = 503
        db_status["message"] = str(e)

    db_latency = time.time() - db_start_time
    db_status["latency"] = round(db_latency, 4)

    return JSONResponse(content={"health": [api_status, db_status]})
