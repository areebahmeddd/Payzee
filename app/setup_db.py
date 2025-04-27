import os
import sys
from pathlib import Path

# Get the absolute path of the project root directory
project_root = Path(__file__).parent.parent.absolute()

# Add the project root to the Python path
sys.path.insert(0, str(project_root))

from app.db_init import init_db, drop_all_tables
from app.database import SessionLocal
from app.seeds.seed import seed_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize the database and seed it with sample data."""
    try:
        # Drop all existing tables
        drop_all_tables()
        
        # Initialize database tables
        init_db()
        
        # Seed the database
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
            
        logger.info("Database setup completed successfully!")
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 