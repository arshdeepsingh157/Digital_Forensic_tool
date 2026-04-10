"""
History Route
View and manage processed files history
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger
from typing import Optional

from models import get_db
from pipeline.storage import StorageService

router = APIRouter()


@router.get("/history")
async def get_file_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    verdict: Optional[str] = Query(None, description="Filter by verdict (Authentic, Suspicious, Tampered)"),
    db: Session = Depends(get_db)
):
    """
    Get history of all processed files
    
    - **skip**: Pagination offset
    - **limit**: Number of results per page
    - **verdict**: Filter by verdict (optional)
    
    Returns paginated list of processed files
    """
    try:
        from models import ForensicFile
        logger.info(f"Fetching file history (skip={skip}, limit={limit}, verdict={verdict})")
        
        files = StorageService.get_all_files(db, skip=skip, limit=limit, verdict=verdict)
        total = db.query(ForensicFile).count()
        
        return {
            "success": True,
            "total": total,
            "skip": skip,
            "limit": limit,
            "returned": len(files),
            "files": [
                {
                    "file_id": f.file_id,
                    "file_name": f.file_name,
                    "file_size": f.file_size,
                    "file_extension": f.file_extension,
                    "overall_score": f.overall_score,
                    "verdict": f.verdict,
                    "confidence": f.confidence,
                    "processed_at": f.processed_at.isoformat() if f.processed_at else None,
                    "status": f.status
                }
                for f in files
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/search")
async def search_files(
    query: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Search files by name or hash
    
    - **query**: Search term (file name or hash)
    
    Returns matching files
    """
    try:
        from models import ForensicFile
        
        files = db.query(ForensicFile).filter(
            (ForensicFile.file_name.contains(query)) |
            (ForensicFile.sha256_hash.contains(query))
        ).limit(50).all()
        
        return {
            "success": True,
            "query": query,
            "results_count": len(files),
            "files": [
                {
                    "file_id": f.file_id,
                    "file_name": f.file_name,
                    "sha256_hash": f.sha256_hash,
                    "overall_score": f.overall_score,
                    "verdict": f.verdict,
                    "processed_at": f.processed_at.isoformat() if f.processed_at else None
                }
                for f in files
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/statistics")
async def get_history_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about processed files
    
    Returns comprehensive statistics
    """
    try:
        stats = StorageService.get_statistics(db)
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/recent")
async def get_recent_files(
    limit: int = Query(10, ge=1, le=100, description="Number of recent files"),
    db: Session = Depends(get_db)
):
    """
    Get most recently processed files
    
    - **limit**: Number of files to return
    
    Returns recent files
    """
    try:
        files = StorageService.get_all_files(db, skip=0, limit=limit)
        
        return {
            "success": True,
            "count": len(files),
            "files": [
                {
                    "file_id": f.file_id,
                    "file_name": f.file_name,
                    "overall_score": f.overall_score,
                    "verdict": f.verdict,
                    "processed_at": f.processed_at.isoformat() if f.processed_at else None
                }
                for f in files
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting recent files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{file_id}")
async def delete_file_record(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a file record from history
    
    - **file_id**: File identifier
    
    Returns deletion result
    """
    try:
        logger.info(f"Deleting file record: {file_id}")
        
        success = StorageService.delete_file(db, file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "message": f"File record {file_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/filter")
async def filter_files(
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum score"),
    file_extension: Optional[str] = Query(None, description="File extension"),
    db: Session = Depends(get_db)
):
    """
    Filter files by various criteria
    
    - **min_score**: Minimum authenticity score
    - **max_score**: Maximum authenticity score
    - **file_extension**: File type filter
    
    Returns filtered files
    """
    try:
        from models import ForensicFile
        
        query = db.query(ForensicFile)
        
        if min_score is not None:
            query = query.filter(ForensicFile.overall_score >= min_score)
        
        if max_score is not None:
            query = query.filter(ForensicFile.overall_score <= max_score)
        
        if file_extension:
            query = query.filter(ForensicFile.file_extension == file_extension)
        
        files = query.limit(100).all()
        
        return {
            "success": True,
            "filters": {
                "min_score": min_score,
                "max_score": max_score,
                "file_extension": file_extension
            },
            "count": len(files),
            "files": [
                {
                    "file_id": f.file_id,
                    "file_name": f.file_name,
                    "file_extension": f.file_extension,
                    "overall_score": f.overall_score,
                    "verdict": f.verdict,
                    "processed_at": f.processed_at.isoformat() if f.processed_at else None
                }
                for f in files
            ]
        }
        
    except Exception as e:
        logger.error(f"Error filtering files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
