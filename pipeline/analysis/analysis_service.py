"""
Analysis Layer
Provides analytics and reporting on forensic data
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from loguru import logger

from models import ForensicFile, ProcessingLog


class AnalysisService:
    """Service for analyzing forensic data and generating insights"""
    
    @staticmethod
    def get_verdict_distribution(db: Session) -> Dict[str, int]:
        """
        Get distribution of verdicts
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with verdict counts
        """
        try:
            results = db.query(
                ForensicFile.verdict,
                func.count(ForensicFile.id).label('count')
            ).group_by(ForensicFile.verdict).all()
            
            return {result.verdict: result.count for result in results}
            
        except Exception as e:
            logger.error(f"Error getting verdict distribution: {str(e)}")
            return {}
    
    @staticmethod
    def get_score_distribution(db: Session, bins: int = 10) -> List[Dict[str, Any]]:
        """
        Get distribution of overall scores
        
        Args:
            db: Database session
            bins: Number of score bins
            
        Returns:
            List of score range counts
        """
        try:
            files = db.query(ForensicFile.overall_score).all()
            scores = [f.overall_score for f in files if f.overall_score is not None]
            
            if not scores:
                return []
            
            # Create bins
            bin_size = 100 / bins
            distribution = []
            
            for i in range(bins):
                range_min = i * bin_size
                range_max = (i + 1) * bin_size
                count = sum(1 for score in scores if range_min <= score < range_max)
                
                distribution.append({
                    "range": f"{range_min:.0f}-{range_max:.0f}",
                    "count": count
                })
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting score distribution: {str(e)}")
            return []
    
    @staticmethod
    def get_temporal_trends(
        db: Session,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get temporal trends in file processing
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            List of daily statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            files = db.query(ForensicFile).filter(
                ForensicFile.processed_at >= start_date
            ).all()
            
            # Group by date
            daily_stats = {}
            
            for file in files:
                if file.processed_at:
                    date_key = file.processed_at.date().isoformat()
                    
                    if date_key not in daily_stats:
                        daily_stats[date_key] = {
                            "date": date_key,
                            "total": 0,
                            "authentic": 0,
                            "suspicious": 0,
                            "tampered": 0
                        }
                    
                    daily_stats[date_key]["total"] += 1
                    
                    if file.verdict == "Authentic":
                        daily_stats[date_key]["authentic"] += 1
                    elif file.verdict == "Suspicious":
                        daily_stats[date_key]["suspicious"] += 1
                    elif file.verdict == "Tampered":
                        daily_stats[date_key]["tampered"] += 1
            
            return sorted(daily_stats.values(), key=lambda x: x["date"])
            
        except Exception as e:
            logger.error(f"Error getting temporal trends: {str(e)}")
            return []
    
    @staticmethod
    def get_top_tampered_files(
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get files with lowest authenticity scores
        
        Args:
            db: Database session
            limit: Number of results to return
            
        Returns:
            List of file information
        """
        try:
            files = db.query(ForensicFile).order_by(
                ForensicFile.overall_score.asc()
            ).limit(limit).all()
            
            return [
                {
                    "file_id": f.file_id,
                    "file_name": f.file_name,
                    "overall_score": f.overall_score,
                    "verdict": f.verdict,
                    "processed_at": f.processed_at.isoformat() if f.processed_at else None
                }
                for f in files
            ]
            
        except Exception as e:
            logger.error(f"Error getting top tampered files: {str(e)}")
            return []
    
    @staticmethod
    def get_processing_performance(db: Session) -> Dict[str, Any]:
        """
        Get processing performance metrics
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            logs = db.query(ProcessingLog).filter(
                ProcessingLog.status == "completed",
                ProcessingLog.duration_seconds.isnot(None)
            ).all()
            
            if not logs:
                return {
                    "total_operations": 0,
                    "avg_duration_seconds": 0,
                    "min_duration_seconds": 0,
                    "max_duration_seconds": 0
                }
            
            durations = [log.duration_seconds for log in logs]
            
            return {
                "total_operations": len(durations),
                "avg_duration_seconds": round(sum(durations) / len(durations), 2),
                "min_duration_seconds": round(min(durations), 2),
                "max_duration_seconds": round(max(durations), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting processing performance: {str(e)}")
            return {}
    
    @staticmethod
    def get_file_type_distribution(db: Session) -> Dict[str, int]:
        """
        Get distribution of file types
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with file type counts
        """
        try:
            results = db.query(
                ForensicFile.file_extension,
                func.count(ForensicFile.id).label('count')
            ).group_by(ForensicFile.file_extension).all()
            
            return {result.file_extension: result.count for result in results}
            
        except Exception as e:
            logger.error(f"Error getting file type distribution: {str(e)}")
            return {}
    
    @staticmethod
    def generate_dashboard_data(db: Session) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with all dashboard metrics
        """
        return {
            "verdict_distribution": AnalysisService.get_verdict_distribution(db),
            "score_distribution": AnalysisService.get_score_distribution(db),
            "temporal_trends": AnalysisService.get_temporal_trends(db, days=30),
            "top_tampered_files": AnalysisService.get_top_tampered_files(db, limit=10),
            "processing_performance": AnalysisService.get_processing_performance(db),
            "file_type_distribution": AnalysisService.get_file_type_distribution(db),
            "generated_at": datetime.utcnow().isoformat()
        }


# Convenience functions
def get_dashboard_data(db: Session) -> Dict[str, Any]:
    """Get complete dashboard data"""
    return AnalysisService.generate_dashboard_data(db)
