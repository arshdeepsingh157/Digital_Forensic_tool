"""
Database Initialization Script
Creates database tables and sets up initial configuration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import init_db, test_postgres_connection, test_mongo_connection
from config.settings import settings
from loguru import logger


def main():
    """Initialize database"""
    
    logger.info("="*60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("="*60)
    
    # Create required directories
    logger.info("Creating required directories...")
    settings.ensure_directories()
    logger.info("✅ Directories created")
    
    # Test PostgreSQL connection
    logger.info("\nTesting PostgreSQL connection...")
    if test_postgres_connection():
        logger.info("✅ PostgreSQL connection successful")
    else:
        logger.error("❌ PostgreSQL connection failed")
        logger.info("Please check your PostgreSQL configuration in .env file")
        return False
    
    # Test MongoDB connection
    logger.info("\nTesting MongoDB connection...")
    if test_mongo_connection():
        logger.info("✅ MongoDB connection successful")
    else:
        logger.warning("⚠️  MongoDB connection failed (optional)")
        logger.info("MongoDB is optional. You can continue without it.")
    
    # Initialize database tables
    logger.info("\nInitializing database tables...")
    try:
        init_db()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
        return False
    
    logger.info("\n" + "="*60)
    logger.info("DATABASE INITIALIZATION COMPLETE")
    logger.info("="*60)
    logger.info("\nYou can now start the application:")
    logger.info("  Backend API:  uvicorn backend.main:app --reload")
    logger.info("  Dashboard:    streamlit run dashboard/app.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
