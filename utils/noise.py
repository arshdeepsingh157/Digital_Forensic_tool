"""
Noise Analysis Module
Detects tampering through pixel-level noise pattern analysis
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple, Dict, Any
from scipy import stats
from loguru import logger


class NoiseAnalysisService:
    """Service for analyzing noise patterns in images"""
    
    @staticmethod
    def extract_noise(image: np.ndarray) -> np.ndarray:
        """
        Extract noise from an image using high-pass filtering
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Noise pattern as numpy array
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to get low-frequency components
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Subtract to get high-frequency components (noise)
        noise = cv2.subtract(gray, blurred)
        
        return noise
    
    @staticmethod
    def calculate_noise_variance(
        image_path: Union[str, Path],
        block_size: int = 64
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Calculate noise variance across image blocks
        
        Args:
            image_path: Path to the image file
            block_size: Size of blocks for analysis
            
        Returns:
            Tuple of (variance map, statistics dictionary)
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Extract noise
            noise = NoiseAnalysisService.extract_noise(img)
            
            # Get dimensions
            height, width = noise.shape
            
            # Calculate number of blocks
            blocks_h = height // block_size
            blocks_w = width // block_size
            
            # Create variance map
            variance_map = np.zeros((blocks_h, blocks_w))
            
            # Calculate variance for each block
            for i in range(blocks_h):
                for j in range(blocks_w):
                    block = noise[
                        i * block_size:(i + 1) * block_size,
                        j * block_size:(j + 1) * block_size
                    ]
                    variance_map[i, j] = np.var(block)
            
            # Calculate statistics
            stats_dict = {
                "mean_variance": float(np.mean(variance_map)),
                "std_variance": float(np.std(variance_map)),
                "min_variance": float(np.min(variance_map)),
                "max_variance": float(np.max(variance_map)),
                "variance_range": float(np.max(variance_map) - np.min(variance_map))
            }
            
            logger.info(f"Noise variance calculated for {image_path.name}")
            
            return variance_map, stats_dict
            
        except Exception as e:
            logger.error(f"Error calculating noise variance: {str(e)}")
            raise
    
    @staticmethod
    def detect_noise_inconsistencies(
        variance_map: np.ndarray,
        threshold_factor: float = 2.0
    ) -> Tuple[np.ndarray, int]:
        """
        Detect regions with inconsistent noise levels
        
        Args:
            variance_map: Variance map from calculate_noise_variance
            threshold_factor: Factor for anomaly detection (default=2.0)
            
        Returns:
            Tuple of (anomaly map, number of anomalous regions)
        """
        try:
            # Calculate mean and std of variance
            mean_var = np.mean(variance_map)
            std_var = np.std(variance_map)
            
            # Identify anomalies (regions with variance significantly different from mean)
            threshold_high = mean_var + (threshold_factor * std_var)
            threshold_low = mean_var - (threshold_factor * std_var)
            
            # Create anomaly map
            anomaly_map = np.zeros_like(variance_map)
            anomaly_map[(variance_map > threshold_high) | (variance_map < threshold_low)] = 1
            
            # Count anomalous regions
            anomaly_count = np.sum(anomaly_map)
            
            logger.info(f"Detected {anomaly_count} anomalous noise regions")
            
            return anomaly_map, int(anomaly_count)
            
        except Exception as e:
            logger.error(f"Error detecting noise inconsistencies: {str(e)}")
            return np.zeros_like(variance_map), 0
    
    @staticmethod
    def visualize_noise_analysis(
        image_path: Union[str, Path],
        variance_map: np.ndarray,
        anomaly_map: np.ndarray
    ) -> str:
        """
        Create visualization of noise analysis results
        
        Args:
            image_path: Original image path
            variance_map: Variance map
            anomaly_map: Anomaly detection map
            
        Returns:
            Path to saved visualization
        """
        try:
            image_path = Path(image_path)
            
            # Normalize variance map for visualization
            variance_vis = cv2.normalize(variance_map, None, 0, 255, cv2.NORM_MINMAX)
            variance_vis = variance_vis.astype(np.uint8)
            variance_vis = cv2.applyColorMap(variance_vis, cv2.COLORMAP_JET)
            
            # Resize anomaly map to match variance map
            anomaly_vis = (anomaly_map * 255).astype(np.uint8)
            anomaly_vis = cv2.resize(anomaly_vis, (variance_vis.shape[1], variance_vis.shape[0]))
            anomaly_vis = cv2.applyColorMap(anomaly_vis, cv2.COLORMAP_HOT)
            
            # Combine visualizations
            combined = np.hstack([variance_vis, anomaly_vis])
            
            # Save visualization
            output_path = image_path.parent / f"noise_analysis_{image_path.stem}.png"
            cv2.imwrite(str(output_path), combined)
            
            logger.info(f"Noise analysis visualization saved to {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            return ""
    
    @staticmethod
    def calculate_noise_score(
        variance_stats: Dict[str, float],
        anomaly_count: int,
        total_blocks: int
    ) -> float:
        """
        Calculate noise-based authenticity score
        
        Args:
            variance_stats: Statistics from noise variance analysis
            anomaly_count: Number of anomalous regions
            total_blocks: Total number of analyzed blocks
            
        Returns:
            Score from 0-100 (higher = more likely authentic)
        """
        try:
            # Base score
            score = 100.0
            
            # Penalize high variance range (indicates inconsistent noise)
            variance_range = variance_stats.get("variance_range", 0)
            std_variance = variance_stats.get("std_variance", 0)
            
            # Normalize penalties
            if std_variance > 0:
                consistency_penalty = min(30, (variance_range / std_variance) * 5)
                score -= consistency_penalty
            
            # Penalize anomalous regions
            if total_blocks > 0:
                anomaly_ratio = anomaly_count / total_blocks
                anomaly_penalty = anomaly_ratio * 40
                score -= anomaly_penalty
            
            # Ensure score is in valid range
            score = max(0, min(100, score))
            
            logger.debug(f"Noise Score: {score:.2f} (anomalies={anomaly_count}/{total_blocks})")
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating noise score: {str(e)}")
            return 50.0  # Return neutral score on error
    
    @staticmethod
    def analyze_image_noise(
        image_path: Union[str, Path],
        block_size: int = 64
    ) -> Dict[str, Any]:
        """
        Perform comprehensive noise analysis
        
        Args:
            image_path: Path to the image file
            block_size: Size of blocks for analysis
            
        Returns:
            Dictionary containing noise analysis results
        """
        try:
            # Calculate noise variance
            variance_map, variance_stats = NoiseAnalysisService.calculate_noise_variance(
                image_path, block_size
            )
            
            # Detect inconsistencies
            anomaly_map, anomaly_count = NoiseAnalysisService.detect_noise_inconsistencies(
                variance_map
            )
            
            # Create visualization
            vis_path = NoiseAnalysisService.visualize_noise_analysis(
                image_path, variance_map, anomaly_map
            )
            
            # Calculate total blocks
            total_blocks = variance_map.shape[0] * variance_map.shape[1]
            
            # Calculate score
            score = NoiseAnalysisService.calculate_noise_score(
                variance_stats, anomaly_count, total_blocks
            )
            
            return {
                "noise_score": round(score, 2),
                "variance_statistics": variance_stats,
                "anomalous_regions": int(anomaly_count),
                "total_regions": int(total_blocks),
                "anomaly_percentage": round((anomaly_count / total_blocks) * 100, 2) if total_blocks > 0 else 0,
                "visualization_path": vis_path,
                "block_size_used": block_size,
                "verdict": NoiseAnalysisService._get_noise_verdict(score)
            }
            
        except Exception as e:
            logger.error(f"Error in noise analysis: {str(e)}")
            return {
                "error": str(e),
                "noise_score": 0.0,
                "verdict": "Error"
            }
    
    @staticmethod
    def _get_noise_verdict(score: float) -> str:
        """Get verdict based on noise score"""
        if score >= 80:
            return "Consistent Noise Pattern"
        elif score >= 50:
            return "Minor Noise Inconsistencies"
        else:
            return "Significant Noise Anomalies"


# Convenience functions
def analyze_noise(image_path: Union[str, Path]) -> Dict[str, Any]:
    """Perform noise analysis on an image"""
    return NoiseAnalysisService.analyze_image_noise(image_path)


def get_noise_score(image_path: Union[str, Path]) -> float:
    """Get noise-based authenticity score"""
    result = NoiseAnalysisService.analyze_image_noise(image_path)
    return result.get("noise_score", 0.0)


# Example usage
if __name__ == "__main__":
    test_image = "sample.jpg"
    
    if Path(test_image).exists():
        result = analyze_noise(test_image)
        print(f"Noise Analysis Results:")
        print(f"  Score: {result['noise_score']}")
        print(f"  Verdict: {result['verdict']}")
        print(f"  Anomalous Regions: {result['anomalous_regions']}/{result['total_regions']}")
