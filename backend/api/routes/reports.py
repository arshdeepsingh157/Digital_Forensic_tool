"""
Reports Route
Generate forensic reports
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from models import get_db
from pipeline.storage import StorageService
from pipeline.analysis import AnalysisService

router = APIRouter()


@router.get("/reports/file/{file_id}")
async def get_forensic_report(
    file_id: str = Path(..., description="Unique file identifier"),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive forensic report for a file
    
    - **file_id**: Unique file identifier
    
    Returns complete forensic analysis report
    """
    try:
        logger.info(f"Generating forensic report for: {file_id}")
        
        forensic_file = StorageService.get_file_by_id(db, file_id)
        
        if not forensic_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        detailed_results = forensic_file.detailed_results or {}
        comprehensive = detailed_results.get("comprehensive_analysis", {})
        
        report = {
            "report_metadata": {
                "report_id": f"RPT-{file_id}",
                "generated_at": datetime.utcnow().isoformat(),
                "report_type": "Digital Forensic Analysis",
                "version": "1.0"
            },
            "file_information": {
                "file_id": forensic_file.file_id,
                "file_name": forensic_file.file_name,
                "file_size": forensic_file.file_size,
                "file_extension": forensic_file.file_extension,
                "sha256_hash": forensic_file.sha256_hash,
                "md5_hash": forensic_file.md5_hash,
                "uploaded_at": forensic_file.uploaded_at.isoformat() if forensic_file.uploaded_at else None,
                "processed_at": forensic_file.processed_at.isoformat() if forensic_file.processed_at else None
            },
            "authenticity_assessment": {
                "overall_score": forensic_file.overall_score,
                "verdict": forensic_file.verdict,
                "confidence_level": forensic_file.confidence,
                "risk_level": StorageService._get_risk_level(forensic_file.overall_score)
            },
            "component_analysis": {
                "metadata_analysis": {
                    "score": forensic_file.metadata_score,
                    "weight": "30%",
                    "camera_make": forensic_file.camera_make,
                    "camera_model": forensic_file.camera_model,
                    "datetime_original": forensic_file.datetime_original,
                    "software": forensic_file.software,
                    "gps_available": forensic_file.has_gps_data
                },
                "hash_verification": {
                    "score": forensic_file.hash_score,
                    "weight": "30%",
                    "sha256": forensic_file.sha256_hash,
                    "integrity_verified": forensic_file.hash_match
                },
                "ela_analysis": {
                    "score": forensic_file.ela_score,
                    "weight": "20%",
                    "tampered_regions": forensic_file.tampered_regions_count,
                    "analysis_available": forensic_file.has_ela_analysis
                },
                "noise_analysis": {
                    "score": forensic_file.noise_score,
                    "weight": "20%",
                    "anomalous_regions": forensic_file.anomaly_count,
                    "analysis_available": forensic_file.has_noise_analysis
                }
            },
            "findings": {
                "tampering_indicators": {
                    "regions_detected": forensic_file.tampered_regions_count,
                    "anomalies_detected": forensic_file.anomaly_count,
                    "total_issues": forensic_file.tampered_regions_count + forensic_file.anomaly_count
                },
                "recommendations": forensic_file.recommendations or []
            },
            "technical_details": comprehensive.get("analysis_components", {}),
            "conclusion": StorageService._generate_conclusion(forensic_file)
        }
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/statistics/overview")
async def get_statistics_report(db: Session = Depends(get_db)):
    """
    Get system-wide statistics report
    
    Returns comprehensive system statistics
    """
    try:
        stats = StorageService.get_statistics(db)
        dashboard_data = AnalysisService.generate_dashboard_data(db)
        
        return {
            "success": True,
            "generated_at": datetime.utcnow().isoformat(),
            "overall_statistics": stats,
            "verdict_distribution": dashboard_data.get("verdict_distribution"),
            "file_type_distribution": dashboard_data.get("file_type_distribution"),
            "performance_metrics": dashboard_data.get("processing_performance"),
            "temporal_trends": dashboard_data.get("temporal_trends")
        }
        
    except Exception as e:
        logger.error(f"Error generating statistics report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/dashboard")
async def get_dashboard_report(db: Session = Depends(get_db)):
    """
    Get dashboard analytics data
    
    Returns all data needed for dashboard visualization
    """
    try:
        dashboard_data = AnalysisService.generate_dashboard_data(db)
        stats = StorageService.get_statistics(db)
        
        return {
            "success": True,
            "kpi": {
                "total_files": stats["total_files"],
                "authentic": stats["authentic"],
                "suspicious": stats["suspicious"],
                "tampered": stats["tampered"],
                "authentic_rate": stats["authentic_percentage"]
            },
            "charts": {
                "verdict_distribution": dashboard_data.get("verdict_distribution"),
                "score_distribution": dashboard_data.get("score_distribution"),
                "temporal_trends": dashboard_data.get("temporal_trends"),
                "file_types": dashboard_data.get("file_type_distribution")
            },
            "performance": dashboard_data.get("processing_performance"),
            "top_tampered": dashboard_data.get("top_tampered_files"),
            "generated_at": dashboard_data.get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper function (add to StorageService if needed)
def _get_risk_level(score: float) -> str:
    """Determine risk level from score"""
    if score >= 90:
        return "Low"
    elif score >= 60:
        return "Medium"
    else:
        return "High"


def _generate_conclusion(forensic_file) -> str:
    """Generate conclusion text"""
    if forensic_file.verdict == "Authentic":
        return f"Based on comprehensive forensic analysis, the file '{forensic_file.file_name}' appears to be authentic with a high confidence level of {forensic_file.confidence}. No significant tampering indicators were detected."
    elif forensic_file.verdict == "Suspicious":
        return f"The file '{forensic_file.file_name}' exhibits some suspicious characteristics. While not definitively tampered, further investigation is recommended. Confidence level: {forensic_file.confidence}."
    else:
        return f"ALERT: The file '{forensic_file.file_name}' shows strong evidence of tampering. Multiple forensic indicators suggest the file has been modified. DO NOT TRUST this file. Confidence level: {forensic_file.confidence}."


# Add these methods to StorageService class
StorageService._get_risk_level = staticmethod(_get_risk_level)
StorageService._generate_conclusion = staticmethod(_generate_conclusion)
