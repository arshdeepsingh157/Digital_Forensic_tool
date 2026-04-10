"""
Configuration Management
Loads environment variables and provides application-wide settings
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra environment variables without raising errors
    )
    
    # ==============================
    # Database Configuration
    # ==============================
    POSTGRES_USER: str = "forensic_user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "forensic_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    MONGO_URI: str = "mongodb://localhost:27017/"
    MONGO_DB: str = "forensic_logs"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # ==============================
    # API Configuration
    # ==============================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_VERSION: str = "v1"
    API_TITLE: str = "AI-Powered Digital Forensics API"
    DEBUG_MODE: bool = True
    
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==============================
    # Storage Configuration
    # ==============================
    STORAGE_PATH: str = "./storage"
    UPLOAD_FOLDER: str = "./storage/uploads"
    PROCESSED_FOLDER: str = "./storage/processed"
    TEMP_FOLDER: str = "./storage/temp"
    
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf,docx,doc"
    
    # ==============================
    # Forensic Analysis Settings
    # ==============================
    ELA_QUALITY: int = 95
    ELA_SCALE: int = 10
    
    AUTHENTIC_THRESHOLD: int = 90
    SUSPICIOUS_THRESHOLD: int = 60
    
    WEIGHT_METADATA: float = 0.30
    WEIGHT_HASH: float = 0.30
    WEIGHT_ELA: float = 0.20
    WEIGHT_NOISE: float = 0.20
    
    # ==============================
    # Airflow Configuration
    # ==============================
    AIRFLOW_HOME: str = "./airflow"
    
    # ==============================
    # Dashboard Configuration
    # ==============================
    DASHBOARD_PORT: int = 8501
    DASHBOARD_THEME: str = "dark"
    
    # ==============================
    # Logging Configuration
    # ==============================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/forensic_system.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"
    
    # ==============================
    # AWS S3 Configuration
    # ==============================
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "forensic-files"
    
    # ==============================
    # Performance Settings
    # ==============================
    WORKER_COUNT: int = 4
    MAX_CONCURRENT_UPLOADS: int = 10
    CACHE_TTL: int = 3600
    
    # ==============================
    # Feature Flags
    # ==============================
    ENABLE_AUTH: bool = False
    ENABLE_RATE_LIMITING: bool = False
    ENABLE_PYSPARK: bool = False
    ENABLE_PDF_REPORTS: bool = True
    
    @property
    def database_url(self) -> str:
        """PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def mongodb_url(self) -> str:
        """MongoDB connection URL"""
        return f"{self.MONGO_URI}{self.MONGO_DB}"
    
    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert allowed extensions string to list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]
    
    def ensure_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.STORAGE_PATH,
            self.UPLOAD_FOLDER,
            self.PROCESSED_FOLDER,
            self.TEMP_FOLDER,
            Path(self.LOG_FILE).parent,
            self.AIRFLOW_HOME
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Create global settings instance
settings = Settings()

# Ensure all required directories exist
settings.ensure_directories()
