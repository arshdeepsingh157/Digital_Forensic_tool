"""
Upload Route
Handles file upload functionality
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime
import shutil
from pathlib import Path

from models import get_db
from pipeline.ingestion import IngestionService
from pipeline.processing import ProcessingService
from pipeline.storage import StorageService
from config.settings import settings

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file for forensic analysis
    
    - **file**: File to analyze (images, PDFs, documents)
    
    Returns analysis results including authenticity score and verdict
    """
    try:
        logger.info(f"Received upload request: {file.filename}")
        
        # Save uploaded file temporarily
        temp_dir = Path(settings.TEMP_FOLDER)
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"upload_{datetime.utcnow().timestamp()}_{file.filename}"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved temporarily: {temp_path}")
        
        # Ingest file
        ingestion_result = IngestionService.ingest_file(temp_path, file.filename)
        
        # Clean up temp file
        temp_path.unlink(missing_ok=True)
        
        if not ingestion_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=ingestion_result.get("error", "File ingestion failed")
            )
        
        file_id = ingestion_result["file_id"]
        file_path = ingestion_result["file_path"]
        
        logger.info(f"File ingested successfully: {file_id}")
        
        # Process file through forensic pipeline
        logger.info(f"Starting forensic analysis for {file_id}")
        processing_result = ProcessingService.process_file(file_path, file_id)
        
        # Save results to database
        forensic_record = StorageService.save_forensic_result(db, processing_result)
        
        # Also save to MongoDB
        StorageService.save_to_mongodb(processing_result)
        
        logger.info(f"Analysis complete for {file_id}")
        
        # Prepare response
        comprehensive = processing_result.get("comprehensive_analysis", {})
        
        return {
            "success": True,
            "message": "File analyzed successfully",
            "file_id": file_id,
            "file_name": file.filename,
            "overall_score": comprehensive.get("overall_score"),
            "verdict": comprehensive.get("verdict"),
            "confidence": comprehensive.get("confidence"),
            "component_scores": comprehensive.get("component_scores"),
            "recommendations": comprehensive.get("recommendations"),
            "processing_time_seconds": processing_result.get("total_duration_seconds"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload/batch")
async def upload_batch(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple files for batch analysis
    
    - **files**: List of files to analyze
    
    Returns list of analysis results
    """
    results = []
    
    for file in files:
        try:
            # Process each file individually
            result = await upload_file(file, db)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            results.append({
                "success": False,
                "file_name": file.filename,
                "error": str(e)
            })
    
    return {
        "success": True,
        "total_files": len(files),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results
    }
