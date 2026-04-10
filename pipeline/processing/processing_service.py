"""
Data Processing Layer
Coordinates forensic analysis execution
"""

from pathlib import Path
from typing import Union, Dict, Any
from datetime import datetime
from loguru import logger

from utils.hashing import HashingService
from utils.ela import ELAService
from utils.metadata import MetadataService
from utils.noise import NoiseAnalysisService
from utils.scorer import AuthenticityScorer
from config.settings import settings


class ProcessingService:
    """Service for processing files through forensic pipeline"""
    
    @staticmethod
    def process_file(
        file_path: Union[str, Path],
        file_id: str,
        original_hash: str = None
    ) -> Dict[str, Any]:
        """
        Process file through complete forensic pipeline
        
        Args:
            file_path: Path to the file
            file_id: Unique file identifier
            original_hash: Original hash for verification (optional)
            
        Returns:
            Dictionary with complete processing results
        """
        file_path = Path(file_path)
        
        logger.info(f"Starting forensic processing for file {file_id}: {file_path.name}")
        
        processing_start = datetime.utcnow()
        
        result = {
            "file_id": file_id,
            "file_name": file_path.name,
            "file_path": str(file_path),
            "processing_start": processing_start.isoformat(),
            "status": "processing",
            "stages": {}
        }
        
        try:
            # Stage 1: Hash Generation
            logger.info(f"[{file_id}] Stage 1: Hash Generation")
            stage_start = datetime.utcnow()
            
            try:
                file_signature = HashingService.generate_file_signature(file_path)
                result["stages"]["hash_generation"] = {
                    "status": "completed",
                    "sha256": file_signature.get("sha256"),
                    "md5": file_signature.get("md5"),
                    "file_size": file_signature.get("file_size"),
                    "duration_seconds": (datetime.utcnow() - stage_start).total_seconds()
                }
                logger.info(f"[{file_id}] Hash generation completed")
            except Exception as e:
                logger.error(f"[{file_id}] Hash generation failed: {str(e)}")
                result["stages"]["hash_generation"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Stage 2: Metadata Extraction
            logger.info(f"[{file_id}] Stage 2: Metadata Extraction")
            stage_start = datetime.utcnow()
            
            try:
                metadata_analysis = MetadataService.analyze_file_metadata(file_path)
                result["stages"]["metadata_extraction"] = {
                    "status": "completed",
                    "metadata_score": metadata_analysis.get("metadata_score"),
                    "verdict": metadata_analysis.get("overall_verdict"),
                    "has_anomalies": metadata_analysis.get("anomaly_detection", {}).get("has_anomalies"),
                    "duration_seconds": (datetime.utcnow() - stage_start).total_seconds()
                }
                logger.info(f"[{file_id}] Metadata extraction completed")
            except Exception as e:
                logger.error(f"[{file_id}] Metadata extraction failed: {str(e)}")
                result["stages"]["metadata_extraction"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Image-specific processing
            file_ext = file_path.suffix.lower()
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                
                # Stage 3: ELA Analysis
                logger.info(f"[{file_id}] Stage 3: ELA Analysis")
                stage_start = datetime.utcnow()
                
                try:
                    ela_analysis = ELAService.analyze_image(file_path)
                    result["stages"]["ela_analysis"] = {
                        "status": "completed",
                        "ela_score": ela_analysis.get("ela_score"),
                        "verdict": ela_analysis.get("verdict"),
                        "tampered_regions": ela_analysis.get("tampered_regions_count"),
                        "duration_seconds": (datetime.utcnow() - stage_start).total_seconds()
                    }
                    logger.info(f"[{file_id}] ELA analysis completed")
                except Exception as e:
                    logger.error(f"[{file_id}] ELA analysis failed: {str(e)}")
                    result["stages"]["ela_analysis"] = {
                        "status": "failed",
                        "error": str(e)
                    }
                
                # Stage 4: Noise Analysis
                logger.info(f"[{file_id}] Stage 4: Noise Analysis")
                stage_start = datetime.utcnow()
                
                try:
                    noise_analysis = NoiseAnalysisService.analyze_image_noise(file_path)
                    result["stages"]["noise_analysis"] = {
                        "status": "completed",
                        "noise_score": noise_analysis.get("noise_score"),
                        "verdict": noise_analysis.get("verdict"),
                        "anomalous_regions": noise_analysis.get("anomalous_regions"),
                        "duration_seconds": (datetime.utcnow() - stage_start).total_seconds()
                    }
                    logger.info(f"[{file_id}] Noise analysis completed")
                except Exception as e:
                    logger.error(f"[{file_id}] Noise analysis failed: {str(e)}")
                    result["stages"]["noise_analysis"] = {
                        "status": "failed",
                        "error": str(e)
                    }
            else:
                logger.info(f"[{file_id}] Skipping image-specific analyses for {file_ext} file")
                result["stages"]["ela_analysis"] = {"status": "skipped", "reason": "Not an image file"}
                result["stages"]["noise_analysis"] = {"status": "skipped", "reason": "Not an image file"}
            
            # Stage 5: Comprehensive Scoring
            logger.info(f"[{file_id}] Stage 5: Comprehensive Scoring")
            stage_start = datetime.utcnow()
            
            try:
                comprehensive_score = AuthenticityScorer.calculate_comprehensive_score(
                    file_path, original_hash
                )
                result["stages"]["scoring"] = {
                    "status": "completed",
                    "overall_score": comprehensive_score.get("overall_score"),
                    "verdict": comprehensive_score.get("verdict"),
                    "confidence": comprehensive_score.get("confidence"),
                    "duration_seconds": (datetime.utcnow() - stage_start).total_seconds()
                }
                
                # Add comprehensive results to main result
                result["comprehensive_analysis"] = comprehensive_score
                
                logger.info(f"[{file_id}] Scoring completed")
            except Exception as e:
                logger.error(f"[{file_id}] Scoring failed: {str(e)}")
                result["stages"]["scoring"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Calculate total processing time
            processing_end = datetime.utcnow()
            result["processing_end"] = processing_end.isoformat()
            result["total_duration_seconds"] = (processing_end - processing_start).total_seconds()
            result["status"] = "completed"
            
            logger.info(f"[{file_id}] Processing completed in {result['total_duration_seconds']:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"[{file_id}] Fatal error during processing: {str(e)}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["processing_end"] = datetime.utcnow().isoformat()
            return result
    
    @staticmethod
    def reprocess_file(file_path: Union[str, Path], file_id: str) -> Dict[str, Any]:
        """
        Reprocess an existing file
        
        Args:
            file_path: Path to the file
            file_id: File identifier
            
        Returns:
            Processing results
        """
        logger.info(f"Reprocessing file {file_id}")
        return ProcessingService.process_file(file_path, file_id)
    
    @staticmethod
    def get_processing_summary(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate processing summary from results
        
        Args:
            result: Processing result dictionary
            
        Returns:
            Summary dictionary
        """
        summary = {
            "file_id": result.get("file_id"),
            "file_name": result.get("file_name"),
            "status": result.get("status"),
            "duration_seconds": result.get("total_duration_seconds"),
            "stages_completed": sum(
                1 for stage in result.get("stages", {}).values()
                if stage.get("status") == "completed"
            ),
            "stages_failed": sum(
                1 for stage in result.get("stages", {}).values()
                if stage.get("status") == "failed"
            )
        }
        
        # Add score if available
        comprehensive = result.get("comprehensive_analysis", {})
        if comprehensive:
            summary["overall_score"] = comprehensive.get("overall_score")
            summary["verdict"] = comprehensive.get("verdict")
            summary["confidence"] = comprehensive.get("confidence")
        
        return summary


# Convenience functions
def process_uploaded_file(file_path: Union[str, Path], file_id: str) -> Dict[str, Any]:
    """Process an uploaded file through the forensic pipeline"""
    return ProcessingService.process_file(file_path, file_id)


def get_summary(processing_result: Dict[str, Any]) -> Dict[str, Any]:
    """Get processing summary"""
    return ProcessingService.get_processing_summary(processing_result)
