"""
Analysis Route
Retrieve forensic analysis results
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from loguru import logger

from models import get_db
from pipeline.storage import StorageService

router = APIRouter()


@router.get("/analysis/{file_id}")
async def get_analysis(
    file_id: str = Path(..., description="Unique file identifier"),
    db: Session = Depends(get_db)
):
    """
    Get forensic analysis results for a specific file
    
    - **file_id**: Unique file identifier
    
    Returns complete analysis results
    """
    try:
        logger.info(f"Retrieving analysis for file: {file_id}")
        
        # Get file from database
        forensic_file = StorageService.get_file_by_id(db, file_id)
        
        if not forensic_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get detailed results from JSON field
        detailed_results = forensic_file.detailed_results or {}
        comprehensive = detailed_results.get("comprehensive_analysis", {})
        
        return {
            "success": True,
            "file_id": forensic_file.file_id,
            "file_name": forensic_file.file_name,
            "file_size": forensic_file.file_size,
            "file_extension": forensic_file.file_extension,
            "sha256_hash": forensic_file.sha256_hash,
            "overall_score": forensic_file.overall_score,
            "verdict": forensic_file.verdict,
            "confidence": forensic_file.confidence,
            "scores": {
                "metadata": forensic_file.metadata_score,
                "hash": forensic_file.hash_score,
                "ela": forensic_file.ela_score,
                "noise": forensic_file.noise_score
            },
            "tampering_indicators": {
                "tampered_regions": forensic_file.tampered_regions_count,
                "anomaly_count": forensic_file.anomaly_count
            },
            "metadata": {
                "camera_make": forensic_file.camera_make,
                "camera_model": forensic_file.camera_model,
                "datetime_original": forensic_file.datetime_original,
                "software": forensic_file.software,
                "has_gps": forensic_file.has_gps_data
            },
            "recommendations": forensic_file.recommendations,
            "processing_info": {
                "status": forensic_file.status,
                "uploaded_at": forensic_file.uploaded_at.isoformat() if forensic_file.uploaded_at else None,
                "processed_at": forensic_file.processed_at.isoformat() if forensic_file.processed_at else None
            },
            "detailed_analysis": comprehensive.get("analysis_components", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{file_id}/summary")
async def get_analysis_summary(
    file_id: str = Path(..., description="Unique file identifier"),
    db: Session = Depends(get_db)
):
    """
    Get brief summary of analysis results
    
    - **file_id**: Unique file identifier
    
    Returns condensed analysis summary
    """
    try:
        forensic_file = StorageService.get_file_by_id(db, file_id)
        
        if not forensic_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "file_id": forensic_file.file_id,
            "file_name": forensic_file.file_name,
            "overall_score": forensic_file.overall_score,
            "verdict": forensic_file.verdict,
            "confidence": forensic_file.confidence,
            "processed_at": forensic_file.processed_at.isoformat() if forensic_file.processed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{file_id}/components")
async def get_component_scores(
    file_id: str = Path(..., description="Unique file identifier"),
    db: Session = Depends(get_db)
):
    """
    Get individual component scores
    
    - **file_id**: Unique file identifier
    
    Returns breakdown of all component scores
    """
    try:
        forensic_file = StorageService.get_file_by_id(db, file_id)
        
        if not forensic_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "file_id": forensic_file.file_id,
            "overall_score": forensic_file.overall_score,
            "components": {
                "metadata": {
                    "score": forensic_file.metadata_score,
                    "weight": "30%",
                    "description": "EXIF data consistency and integrity"
                },
                "hash": {
                    "score": forensic_file.hash_score,
                    "weight": "30%",
                    "description": "SHA-256 cryptographic verification"
                },
                "ela": {
                    "score": forensic_file.ela_score,
                    "weight": "20%",
                    "description": "Error Level Analysis - compression artifacts"
                },
                "noise": {
                    "score": forensic_file.noise_score,
                    "weight": "20%",
                    "description": "Noise pattern consistency analysis"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving components: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
