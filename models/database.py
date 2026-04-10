"""
Database Connection and Session Management
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pymongo import MongoClient
from loguru import logger
from typing import Generator

from config.settings import settings
from .postgres_models import Base

# PostgreSQL Engine (Optional - runs without if psycopg2 not installed)
try:
    engine = create_engine(
        settings.database_url,
        echo=settings.DEBUG_MODE,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20
    )
    # Session Factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("PostgreSQL engine created successfully")
    POSTGRES_AVAILABLE = True
except Exception as e:
    logger.warning(f"PostgreSQL not available: {e}")
    logger.warning("Running in limited mode without PostgreSQL")
    engine = None
    SessionLocal = None
    POSTGRES_AVAILABLE = False


def init_db():
    """Initialize database - create all tables"""
    if not POSTGRES_AVAILABLE:
        logger.warning("PostgreSQL not available - skipping database initialization")
        return
    
    try:
        logger.info("Initializing PostgreSQL database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for database session
    
    Get database session for dependency injection
    
    Usage:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    if not POSTGRES_AVAILABLE or SessionLocal is None:
        logger.warning("PostgreSQL not available")
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MongoDB Connection
try:
    mongo_client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_db = mongo_client[settings.MONGO_DB]
    logger.info("MongoDB connection established")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")
    mongo_db = None


def get_mongo_db():
    """Get MongoDB database instance"""
    if mongo_db is None:
        logger.error("MongoDB not available")
        raise Exception("MongoDB connection not available")
    return mongo_db


# MongoDB Collections
class MongoCollections:
    """MongoDB collection names"""
    
    FORENSIC_REPORTS = "forensic_reports"
    DETAILED_LOGS = "detailed_logs"
    AUDIT_TRAIL = "audit_trail"
    PROCESSING_EVENTS = "processing_events"


def get_collection(collection_name: str):
    """Get MongoDB collection by name"""
    db = get_mongo_db()
    return db[collection_name]


# Utility Functions
def test_postgres_connection() -> bool:
    """Test PostgreSQL connection"""
    try:
        if engine is None:
            logger.error("PostgreSQL engine is not initialized")
            return False
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("PostgreSQL connection test successful")
            return True
    except Exception as e:
        logger.error(f"PostgreSQL connection test failed: {str(e)}")
        return False


def test_mongo_connection() -> bool:
    """Test MongoDB connection"""
    try:
        mongo_client.server_info()
        logger.info("MongoDB connection test successful")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {str(e)}")
        return False


def close_connections():
    """Close all database connections"""
    try:
        engine.dispose()
        if mongo_client:
            mongo_client.close()
        logger.info("All database connections closed")
    except Exception as e:
        logger.error(f"Error closing connections: {str(e)}")
