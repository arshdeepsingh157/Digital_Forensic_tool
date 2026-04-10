"""
Error Level Analysis (ELA)
Detects image tampering by analyzing compression artifacts
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple, Optional
from PIL import Image
from loguru import logger


class ELAService:
    """Service for performing Error Level Analysis on images"""
    
    DEFAULT_QUALITY = 95
    DEFAULT_SCALE = 10
    
    @staticmethod
    def perform_ela(
        image_path: Union[str, Path],
        quality: int = DEFAULT_QUALITY,
        scale: int = DEFAULT_SCALE
    ) -> Tuple[np.ndarray, str]:
        """
        Perform Error Level Analysis on an image
        
        Args:
            image_path: Path to the image file
            quality: JPEG compression quality (1-100, default=95)
            scale: Difference amplification scale (default=10)
            
        Returns:
            Tuple of (ELA image as numpy array, path to saved ELA image)
            
        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If image cannot be processed
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            # Open original image
            original_img = Image.open(image_path).convert('RGB')
            
            # Save with specified quality to temporary file
            temp_path = image_path.parent / f"temp_{image_path.stem}.jpg"
            original_img.save(temp_path, 'JPEG', quality=quality)
            
            # Reopen compressed image
            compressed_img = Image.open(temp_path).convert('RGB')
            
            # Convert to numpy arrays
            original_array = np.array(original_img, dtype=np.float32)
            compressed_array = np.array(compressed_img, dtype=np.float32)
            
            # Calculate difference
            diff = np.abs(original_array - compressed_array) * scale
            
            # Clip values to valid range
            ela_image = np.clip(diff, 0, 255).astype(np.uint8)
            
            # Save ELA result
            output_path = image_path.parent / f"ela_{image_path.stem}.png"
            cv2.imwrite(str(output_path), cv2.cvtColor(ela_image, cv2.COLOR_RGB2BGR))
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            logger.info(f"ELA performed on {image_path.name}, saved to {output_path.name}")
            
            return ela_image, str(output_path)
            
        except Exception as e:
            logger.error(f"Error performing ELA on {image_path}: {str(e)}")
            raise ValueError(f"Failed to perform ELA: {str(e)}")
    
    @staticmethod
    def calculate_ela_score(ela_image: np.ndarray) -> float:
        """
        Calculate tampering score based on ELA results
        
        Args:
            ela_image: ELA result as numpy array
            
        Returns:
            Score from 0-100 (higher = more likely authentic)
        """
        try:
            # Convert to grayscale if needed
            if len(ela_image.shape) == 3:
                gray_ela = cv2.cvtColor(ela_image, cv2.COLOR_RGB2GRAY)
            else:
                gray_ela = ela_image
            
            # Calculate statistics
            mean_intensity = np.mean(gray_ela)
            std_intensity = np.std(gray_ela)
            max_intensity = np.max(gray_ela)
            
            # High variance in ELA indicates tampering
            # Low variance indicates consistent compression (authentic)
            
            # Normalize score (inverted: lower variance = higher score)
            # Range: 0-100
            variance_score = max(0, 100 - (std_intensity / 2.55))
            
            # Penalize high maximum values (indicates strong differences)
            max_penalty = (max_intensity / 255) * 30
            
            # Penalize high mean (indicates overall high differences)
            mean_penalty = (mean_intensity / 255) * 20
            
            final_score = variance_score - max_penalty - mean_penalty
            final_score = max(0, min(100, final_score))
            
            logger.debug(f"ELA Score: {final_score:.2f} (mean={mean_intensity:.2f}, std={std_intensity:.2f})")
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating ELA score: {str(e)}")
            return 50.0  # Return neutral score on error
    
    @staticmethod
    def detect_tampered_regions(
        ela_image: np.ndarray,
        threshold: int = 30
    ) -> Tuple[np.ndarray, list]:
        """
        Detect potentially tampered regions in ELA image
        
        Args:
            ela_image: ELA result as numpy array
            threshold: Intensity threshold for detecting tampering
            
        Returns:
            Tuple of (annotated image, list of bounding boxes)
        """
        try:
            # Convert to grayscale
            if len(ela_image.shape) == 3:
                gray_ela = cv2.cvtColor(ela_image, cv2.COLOR_RGB2GRAY)
            else:
                gray_ela = ela_image
            
            # Threshold to find high-error regions
            _, binary = cv2.threshold(gray_ela, threshold, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter small contours (noise)
            min_area = 100
            significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
            
            # Create annotated image
            annotated = ela_image.copy()
            bounding_boxes = []
            
            for contour in significant_contours:
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append({'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)})
                
                # Draw rectangle on annotated image
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            logger.info(f"Detected {len(bounding_boxes)} potentially tampered regions")
            
            return annotated, bounding_boxes
            
        except Exception as e:
            logger.error(f"Error detecting tampered regions: {str(e)}")
            return ela_image, []
    
    @staticmethod
    def analyze_image(
        image_path: Union[str, Path],
        quality: int = DEFAULT_QUALITY,
        scale: int = DEFAULT_SCALE
    ) -> dict:
        """
        Perform comprehensive ELA analysis
        
        Args:
            image_path: Path to the image file
            quality: JPEG compression quality
            scale: Difference amplification scale
            
        Returns:
            Dictionary containing ELA results and analysis
        """
        try:
            # Perform ELA
            ela_image, ela_path = ELAService.perform_ela(image_path, quality, scale)
            
            # Calculate score
            score = ELAService.calculate_ela_score(ela_image)
            
            # Detect tampered regions
            annotated_image, regions = ELAService.detect_tampered_regions(ela_image)
            
            # Save annotated image
            annotated_path = Path(image_path).parent / f"ela_annotated_{Path(image_path).stem}.png"
            cv2.imwrite(str(annotated_path), cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
            
            return {
                "ela_score": round(score, 2),
                "ela_image_path": ela_path,
                "annotated_image_path": str(annotated_path),
                "tampered_regions": regions,
                "tampered_regions_count": len(regions),
                "quality_used": quality,
                "scale_used": scale,
                "verdict": ELAService._get_verdict(score)
            }
            
        except Exception as e:
            logger.error(f"Error in ELA analysis: {str(e)}")
            return {
                "error": str(e),
                "ela_score": 0.0,
                "verdict": "Error"
            }
    
    @staticmethod
    def _get_verdict(score: float) -> str:
        """Get verdict based on ELA score"""
        if score >= 80:
            return "Likely Authentic"
        elif score >= 50:
            return "Suspicious"
        else:
            return "Likely Tampered"


# Convenience functions
def analyze_image_ela(image_path: Union[str, Path]) -> dict:
    """Perform ELA analysis on an image"""
    return ELAService.analyze_image(image_path)


def get_ela_score(image_path: Union[str, Path]) -> float:
    """Get ELA score for an image"""
    ela_image, _ = ELAService.perform_ela(image_path)
    return ELAService.calculate_ela_score(ela_image)


# Example usage
if __name__ == "__main__":
    test_image = "sample.jpg"
    
    if Path(test_image).exists():
        result = analyze_image_ela(test_image)
        print(f"ELA Analysis Results:")
        print(f"  Score: {result['ela_score']}")
        print(f"  Verdict: {result['verdict']}")
        print(f"  Tampered Regions: {result['tampered_regions_count']}")
