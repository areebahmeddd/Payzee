from fastapi import FastAPI
from . import models
from .database import engine
from .routes import router
from .db_init import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
try:
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully!")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    raise

app = FastAPI(
    title="Payzee API",
    description="API for managing users, vendors, schemes, and transactions",
    version="1.0.0"
)

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Payzee API"} 