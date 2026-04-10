"""
Authenticity Scoring System
Combines multiple forensic analyses to generate overall authenticity score
"""

from pathlib import Path
from typing import Union, Dict, Any
from loguru import logger

from .hashing import HashingService
from .ela import ELAService
from .metadata import MetadataService
from .noise import NoiseAnalysisService
from config.settings import settings


class AuthenticityScorer:
    """
    Combines multiple forensic techniques to calculate authenticity score
    
    Scoring Algorithm:
    - Metadata Integrity: 30%
    - Hash Verification: 30%
    - ELA Analysis: 20%
    - Noise Analysis: 20%
    """
    
    # Weights from configuration
    WEIGHT_METADATA = settings.WEIGHT_METADATA
    WEIGHT_HASH = settings.WEIGHT_HASH
    WEIGHT_ELA = settings.WEIGHT_ELA
    WEIGHT_NOISE = settings.WEIGHT_NOISE
    
    # Thresholds
    AUTHENTIC_THRESHOLD = settings.AUTHENTIC_THRESHOLD
    SUSPICIOUS_THRESHOLD = settings.SUSPICIOUS_THRESHOLD
    
    @staticmethod
    def calculate_comprehensive_score(
        file_path: Union[str, Path],
        original_hash: str = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive authenticity score
        
        Args:
            file_path: Path to the file to analyze
            original_hash: Original SHA-256 hash for verification (optional)
            
        Returns:
            Dictionary with complete analysis results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {
                "error": "File not found",
                "overall_score": 0,
                "verdict": "Error"
            }
        
        logger.info(f"Starting comprehensive analysis for {file_path.name}")
        
        # Initialize results
        results = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "analysis_components": {},
            "component_scores": {},
            "weighted_scores": {}
        }
        
        try:
            # 1. Metadata Analysis (30%)
            logger.info("Performing metadata analysis...")
            metadata_analysis = MetadataService.analyze_file_metadata(file_path)
            metadata_score = metadata_analysis.get("metadata_score", 0)
            
            results["analysis_components"]["metadata"] = metadata_analysis
            results["component_scores"]["metadata"] = metadata_score
            results["weighted_scores"]["metadata"] = metadata_score * AuthenticityScorer.WEIGHT_METADATA
            
        except Exception as e:
            logger.error(f"Metadata analysis failed: {str(e)}")
            results["component_scores"]["metadata"] = 0
            results["weighted_scores"]["metadata"] = 0
        
        try:
            # 2. Hash Verification (30%)
            logger.info("Performing hash analysis...")
            hash_score = HashingService.calculate_score(file_path, original_hash)
            file_hash = HashingService.calculate_sha256(file_path)
            
            results["analysis_components"]["hash"] = {
                "file_hash": file_hash,
                "original_hash": original_hash,
                "match": hash_score == 100,
                "hash_score": hash_score
            }
            results["component_scores"]["hash"] = hash_score
            results["weighted_scores"]["hash"] = hash_score * AuthenticityScorer.WEIGHT_HASH
            
        except Exception as e:
            logger.error(f"Hash analysis failed: {str(e)}")
            results["component_scores"]["hash"] = 0
            results["weighted_scores"]["hash"] = 0
        
        # Image-specific analyses (only for image files)
        file_ext = file_path.suffix.lower()
        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            try:
                # 3. ELA Analysis (20%)
                logger.info("Performing ELA analysis...")
                ela_analysis = ELAService.analyze_image(file_path)
                ela_score = ela_analysis.get("ela_score", 0)
                
                results["analysis_components"]["ela"] = ela_analysis
                results["component_scores"]["ela"] = ela_score
                results["weighted_scores"]["ela"] = ela_score * AuthenticityScorer.WEIGHT_ELA
                
            except Exception as e:
                logger.error(f"ELA analysis failed: {str(e)}")
                results["component_scores"]["ela"] = 50  # Neutral score for non-image
                results["weighted_scores"]["ela"] = 50 * AuthenticityScorer.WEIGHT_ELA
            
            try:
                # 4. Noise Analysis (20%)
                logger.info("Performing noise analysis...")
                noise_analysis = NoiseAnalysisService.analyze_image_noise(file_path)
                noise_score = noise_analysis.get("noise_score", 0)
                
                results["analysis_components"]["noise"] = noise_analysis
                results["component_scores"]["noise"] = noise_score
                results["weighted_scores"]["noise"] = noise_score * AuthenticityScorer.WEIGHT_NOISE
                
            except Exception as e:
                logger.error(f"Noise analysis failed: {str(e)}")
                results["component_scores"]["noise"] = 50  # Neutral score
                results["weighted_scores"]["noise"] = 50 * AuthenticityScorer.WEIGHT_NOISE
        else:
            # Non-image files: assign neutral scores to image-specific analyses
            logger.info(f"Skipping image-specific analyses for {file_ext} file")
            results["component_scores"]["ela"] = 50
            results["weighted_scores"]["ela"] = 50 * AuthenticityScorer.WEIGHT_ELA
            results["component_scores"]["noise"] = 50
            results["weighted_scores"]["noise"] = 50 * AuthenticityScorer.WEIGHT_NOISE
        
        # Calculate overall score
        overall_score = sum(results["weighted_scores"].values())
        results["overall_score"] = round(overall_score, 2)
        
        # Determine verdict
        results["verdict"] = AuthenticityScorer._get_verdict(overall_score)
        results["confidence"] = AuthenticityScorer._calculate_confidence(results["component_scores"])
        
        # Add recommendations
        results["recommendations"] = AuthenticityScorer._generate_recommendations(results)
        
        logger.info(f"Analysis complete. Overall score: {overall_score:.2f} - {results['verdict']}")
        
        return results
    
    @staticmethod
    def _get_verdict(score: float) -> str:
        """Get authenticity verdict based on score"""
        if score >= AuthenticityScorer.AUTHENTIC_THRESHOLD:
            return "Authentic"
        elif score >= AuthenticityScorer.SUSPICIOUS_THRESHOLD:
            return "Suspicious"
        else:
            return "Tampered"
    
    @staticmethod
    def _calculate_confidence(component_scores: Dict[str, float]) -> str:
        """
        Calculate confidence level based on score agreement
        
        Args:
            component_scores: Dictionary of individual component scores
            
        Returns:
            Confidence level (High, Medium, Low)
        """
        scores = list(component_scores.values())
        
        if not scores:
            return "Low"
        
        # Calculate standard deviation
        import numpy as np
        std_dev = np.std(scores)
        
        # Low std dev = high agreement = high confidence
        if std_dev < 15:
            return "High"
        elif std_dev < 30:
            return "Medium"
        else:
            return "Low"
    
    @staticmethod
    def _generate_recommendations(results: Dict[str, Any]) -> list:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Check metadata score
        metadata_score = results["component_scores"].get("metadata", 0)
        if metadata_score < 60:
            recommendations.append("Metadata shows significant inconsistencies. Verify source authenticity.")
        
        # Check hash score
        hash_score = results["component_scores"].get("hash", 0)
        if hash_score < 100 and results["analysis_components"].get("hash", {}).get("original_hash"):
            recommendations.append("File hash does not match original. File has been modified.")
        
        # Check ELA score
        ela_score = results["component_scores"].get("ela", 0)
        if ela_score < 60:
            recommendations.append("ELA analysis detected compression inconsistencies. Manual review recommended.")
        
        # Check noise score
        noise_score = results["component_scores"].get("noise", 0)
        if noise_score < 60:
            recommendations.append("Noise pattern inconsistencies detected. Possible tampering in specific regions.")
        
        # Overall verdict
        if results["verdict"] == "Tampered":
            recommendations.append("Overall analysis indicates high likelihood of tampering. DO NOT TRUST.")
        elif results["verdict"] == "Suspicious":
            recommendations.append("File shows suspicious characteristics. Further investigation recommended.")
        
        if not recommendations:
            recommendations.append("File appears authentic based on all forensic analyses.")
        
        return recommendations


# Convenience function
def analyze_file_authenticity(
    file_path: Union[str, Path],
    original_hash: str = None
) -> Dict[str, Any]:
    """
    Analyze file authenticity using all available forensic techniques
    
    Args:
        file_path: Path to the file
        original_hash: Original hash for verification (optional)
        
    Returns:
        Dictionary with comprehensive analysis results
    """
    return AuthenticityScorer.calculate_comprehensive_score(file_path, original_hash)


# Example usage
if __name__ == "__main__":
    test_file = "sample.jpg"
    
    if Path(test_file).exists():
        results = analyze_file_authenticity(test_file)
        print(f"\n{'='*60}")
        print(f"FORENSIC ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"File: {results['file_name']}")
        print(f"\nComponent Scores:")
        for component, score in results['component_scores'].items():
            print(f"  {component.capitalize()}: {score:.2f}")
        print(f"\nOverall Score: {results['overall_score']:.2f}")
        print(f"Verdict: {results['verdict']}")
        print(f"Confidence: {results['confidence']}")
        print(f"\nRecommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"  {i}. {rec}")
        print(f"{'='*60}\n")
