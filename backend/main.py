"""
FastAPI Main Application
AI-Powered Digital Forensics System API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
from datetime import datetime

from config.settings import settings
from models import init_db
from backend.api.routes import upload, analysis, verification, reports, history

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    settings.LOG_FILE,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    level=settings.LOG_LEVEL
)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Production-ready AI-powered digital forensics platform for detecting file tampering and ensuring digital authenticity",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG_MODE else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting AI-Powered Digital Forensics System API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    logger.info(f"API started successfully on {settings.API_HOST}:{settings.API_PORT}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")
    from models import close_connections
    close_connections()
    logger.info("API shutdown complete")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "online",
        "service": "AI-Powered Digital Forensics System",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    from models import test_postgres_connection, test_mongo_connection
    
    postgres_status = test_postgres_connection()
    mongo_status = test_mongo_connection()
    
    return {
        "status": "healthy" if (postgres_status and mongo_status) else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "postgres": "connected" if postgres_status else "disconnected",
            "mongodb": "connected" if mongo_status else "disconnected"
        }
    }


# Include routers
app.include_router(upload.router, prefix=f"/api/{settings.API_VERSION}", tags=["Upload"])
app.include_router(analysis.router, prefix=f"/api/{settings.API_VERSION}", tags=["Analysis"])
app.include_router(verification.router, prefix=f"/api/{settings.API_VERSION}", tags=["Verification"])
app.include_router(reports.router, prefix=f"/api/{settings.API_VERSION}", tags=["Reports"])
app.include_router(history.router, prefix=f"/api/{settings.API_VERSION}", tags=["History"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG_MODE,
        log_level=settings.LOG_LEVEL.lower()
    )
