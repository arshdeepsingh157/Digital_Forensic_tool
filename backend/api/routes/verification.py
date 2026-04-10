"""
Verification Route
File integrity verification endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger
from pathlib import Path
import shutil
from datetime import datetime

from models import get_db
from pipeline.storage import StorageService
from utils.hashing import HashingService
from config.settings import settings

router = APIRouter()


class HashVerificationRequest(BaseModel):
    """Request model for hash verification"""
    file_id: str
    expected_hash: str


@router.post("/verify/hash")
async def verify_file_hash(
    request: HashVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify file integrity using SHA-256 hash
    
    - **file_id**: File identifier
    - **expected_hash**: Expected SHA-256 hash value
    
    Returns verification result
    """
    try:
        logger.info(f"Verifying hash for file: {request.file_id}")
        
        # Get file from database
        forensic_file = StorageService.get_file_by_id(db, request.file_id)
        
        if not forensic_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Compare hashes
        actual_hash = forensic_file.sha256_hash
        match = actual_hash.lower() == request.expected_hash.lower()
        
        # Save integrity check
        StorageService.save_integrity_check(
            db=db,
            file_id=request.file_id,
            expected_hash=request.expected_hash,
            actual_hash=actual_hash,
            match=match
        )
        
        return {
            "success": True,
            "file_id": request.file_id,
            "file_name": forensic_file.file_name,
            "match": match,
            "expected_hash": request.expected_hash,
            "actual_hash": actual_hash,
            "verdict": "Intact" if match else "Modified",
            "message": "File integrity verified successfully" if match else "File has been modified",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying hash: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify/upload")
async def verify_uploaded_file(
    file: UploadFile = File(...),
    expected_hash: str = None,
    db: Session = Depends(get_db)
):
    """
    Verify integrity of an uploaded file
    
    - **file**: File to verify
    - **expected_hash**: Expected SHA-256 hash (optional)
    
    Returns hash and verification result
    """
    try:
        logger.info(f"Verifying uploaded file: {file.filename}")
        
        # Save file temporarily
        temp_dir = Path(settings.TEMP_FOLDER)
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"verify_{datetime.utcnow().timestamp()}_{file.filename}"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Calculate hash
        actual_hash = HashingService.calculate_sha256(temp_path)
        
        # Clean up
        temp_path.unlink(missing_ok=True)
        
        result = {
            "success": True,
            "file_name": file.filename,
            "sha256_hash": actual_hash
        }
        
        # If expected hash provided, verify
        if expected_hash:
            match = actual_hash.lower() == expected_hash.lower()
            result.update({
                "verification": {
                    "match": match,
                    "expected_hash": expected_hash,
                    "verdict": "Intact" if match else "Modified"
                }
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/file/{file_id}")
async def get_file_hash(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get SHA-256 hash for a file
    
    - **file_id**: File identifier
    
    Returns file hash information
    """
    try:
        forensic_file = StorageService.get_file_by_id(db, file_id)
        
        if not forensic_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "file_id": forensic_file.file_id,
            "file_name": forensic_file.file_name,
            "sha256_hash": forensic_file.sha256_hash,
            "md5_hash": forensic_file.md5_hash,
            "file_size": forensic_file.file_size,
            "uploaded_at": forensic_file.uploaded_at.isoformat() if forensic_file.uploaded_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file hash: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/history/{file_id}")
async def get_verification_history(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get verification history for a file
    
    - **file_id**: File identifier
    
    Returns list of all verification checks
    """
    try:
        from models import IntegrityCheck
        
        checks = db.query(IntegrityCheck).filter(
            IntegrityCheck.file_id == file_id
        ).order_by(IntegrityCheck.checked_at.desc()).all()
        
        return {
            "success": True,
            "file_id": file_id,
            "total_checks": len(checks),
            "checks": [
                {
                    "checked_at": check.checked_at.isoformat(),
                    "match": check.match,
                    "expected_hash": check.expected_hash,
                    "actual_hash": check.actual_hash,
                    "checked_by": check.checked_by
                }
                for check in checks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting verification history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
