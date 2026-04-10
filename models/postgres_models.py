"""
PostgreSQL Database Models
Structured data storage for forensic analysis results
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ForensicFile(Base):
    """Model for storing file information and analysis results"""
    
    __tablename__ = "forensic_files"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(String(64), unique=True, index=True, nullable=False)  # UUID
    
    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_extension = Column(String(10), nullable=False)
    mime_type = Column(String(100))
    
    # Hash Values
    sha256_hash = Column(String(64), index=True, nullable=False)
    md5_hash = Column(String(32))
    original_hash = Column(String(64))  # For integrity verification
    hash_match = Column(Boolean, default=None)
    
    # Overall Scores
    overall_score = Column(Float, nullable=False)
    metadata_score = Column(Float)
    hash_score = Column(Float)
    ela_score = Column(Float)
    noise_score = Column(Float)
    
    # Verdict
    verdict = Column(String(20), index=True)  # Authentic, Suspicious, Tampered
    confidence = Column(String(20))  # High, Medium, Low
    
    # Analysis Flags
    has_metadata = Column(Boolean, default=False)
    has_gps_data = Column(Boolean, default=False)
    has_ela_analysis = Column(Boolean, default=False)
    has_noise_analysis = Column(Boolean, default=False)
    
    # Tampering Detection
    tampered_regions_count = Column(Integer, default=0)
    anomaly_count = Column(Integer, default=0)
    
    # Metadata Fields (Key fields stored separately for querying)
    camera_make = Column(String(100))
    camera_model = Column(String(100))
    datetime_original = Column(String(50))
    software = Column(String(100))
    
    # Processing Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User Information (optional, for multi-user systems)
    uploaded_by = Column(String(100))
    
    # Additional Data (JSON for flexibility)
    recommendations = Column(JSON)
    detailed_results = Column(JSON)
    
    def __repr__(self):
        return f"<ForensicFile(id={self.id}, file_name='{self.file_name}', verdict='{self.verdict}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_extension": self.file_extension,
            "sha256_hash": self.sha256_hash,
            "overall_score": self.overall_score,
            "metadata_score": self.metadata_score,
            "hash_score": self.hash_score,
            "ela_score": self.ela_score,
            "noise_score": self.noise_score,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "tampered_regions_count": self.tampered_regions_count,
            "status": self.status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class ProcessingLog(Base):
    """Model for logging processing pipeline activities"""
    
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(String(64), index=True, nullable=False)
    
    # Processing Information
    stage = Column(String(50), nullable=False)  # ingestion, processing, analysis, storage
    status = Column(String(20), nullable=False)  # started, completed, failed
    message = Column(Text)
    error_details = Column(Text)
    
    # Performance Metrics
    duration_seconds = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ProcessingLog(file_id='{self.file_id}', stage='{self.stage}', status='{self.status}')>"


class IntegrityCheck(Base):
    """Model for file integrity verification history"""
    
    __tablename__ = "integrity_checks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(String(64), index=True, nullable=False)
    
    # Verification Details
    expected_hash = Column(String(64), nullable=False)
    actual_hash = Column(String(64), nullable=False)
    match = Column(Boolean, nullable=False)
    
    # Request Information
    checked_by = Column(String(100))
    ip_address = Column(String(45))
    
    # Timestamp
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<IntegrityCheck(file_id='{self.file_id}', match={self.match})>"


class SystemMetrics(Base):
    """Model for system performance and usage metrics"""
    
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Metrics
    total_files_processed = Column(Integer, default=0)
    total_authentic = Column(Integer, default=0)
    total_suspicious = Column(Integer, default=0)
    total_tampered = Column(Integer, default=0)
    
    # Performance
    avg_processing_time_seconds = Column(Float)
    total_storage_used_mb = Column(Float)
    
    # Period
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    period = Column(String(20))  # daily, weekly, monthly
    
    def __repr__(self):
        return f"<SystemMetrics(date='{self.date}', total_files={self.total_files_processed})>"
