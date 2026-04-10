"""
Metadata Extraction and Analysis
Extracts and analyzes EXIF and other metadata from digital files
"""

import exifread
import piexif
from pathlib import Path
from typing import Union, Dict, Any, Optional
from datetime import datetime
from PIL import Image
from loguru import logger


class MetadataService:
    """Service for extracting and analyzing file metadata"""
    
    @staticmethod
    def extract_exif_data(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract EXIF data from an image file
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing EXIF data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {}
        
        exif_data = {}
        
        try:
            # Method 1: Using exifread
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                for tag, value in tags.items():
                    # Convert to string for JSON serialization
                    exif_data[tag] = str(value)
            
            logger.info(f"Extracted {len(exif_data)} EXIF tags from {file_path.name}")
            
        except Exception as e:
            logger.warning(f"Error extracting EXIF with exifread: {str(e)}")
            
            # Method 2: Fallback to PIL
            try:
                img = Image.open(file_path)
                exif_dict = img._getexif() if hasattr(img, '_getexif') else {}
                
                if exif_dict:
                    for tag_id, value in exif_dict.items():
                        try:
                            tag_name = piexif.TAGS.get(tag_id, {}).get('name', f'Tag_{tag_id}')
                            exif_data[tag_name] = str(value)
                        except:
                            pass
                            
            except Exception as e2:
                logger.error(f"Error extracting EXIF with PIL: {str(e2)}")
        
        return exif_data
    
    @staticmethod
    def extract_key_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract key metadata fields for forensic analysis
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with key metadata fields
        """
        file_path = Path(file_path)
        exif_data = MetadataService.extract_exif_data(file_path)
        
        # Extract commonly used fields
        metadata = {
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "file_extension": file_path.suffix.lower(),
            "camera_make": exif_data.get("Image Make", "N/A"),
            "camera_model": exif_data.get("Image Model", "N/A"),
            "datetime_original": exif_data.get("EXIF DateTimeOriginal", "N/A"),
            "datetime_digitized": exif_data.get("EXIF DateTimeDigitized", "N/A"),
            "software": exif_data.get("Image Software", "N/A"),
            "gps_latitude": exif_data.get("GPS GPSLatitude", "N/A"),
            "gps_longitude": exif_data.get("GPS GPSLongitude", "N/A"),
            "image_width": exif_data.get("EXIF ExifImageWidth", "N/A"),
            "image_height": exif_data.get("EXIF ExifImageLength", "N/A"),
            "orientation": exif_data.get("Image Orientation", "N/A"),
            "x_resolution": exif_data.get("Image XResolution", "N/A"),
            "y_resolution": exif_data.get("Image YResolution", "N/A"),
        }
        
        return metadata
    
    @staticmethod
    def analyze_metadata_consistency(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze metadata for inconsistencies that might indicate tampering
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Dictionary with consistency analysis results
        """
        issues = []
        warnings = []
        score = 100.0
        
        # Check for missing critical fields
        critical_fields = ["camera_make", "camera_model", "datetime_original"]
        missing_fields = [field for field in critical_fields 
                         if metadata.get(field) in ["N/A", "", None]]
        
        if missing_fields:
            issues.append(f"Missing critical metadata: {', '.join(missing_fields)}")
            score -= len(missing_fields) * 10
        
        # Check for software modifications
        software = metadata.get("software", "")
        if software != "N/A" and any(editor in software.lower() 
                                    for editor in ["photoshop", "gimp", "paint", "editor"]):
            warnings.append(f"Image edited with: {software}")
            score -= 15
        
        # Check datetime consistency
        datetime_original = metadata.get("datetime_original", "N/A")
        datetime_digitized = metadata.get("datetime_digitized", "N/A")
        
        if datetime_original != "N/A" and datetime_digitized != "N/A":
            if datetime_original != datetime_digitized:
                warnings.append("Original and digitized timestamps differ")
                score -= 5
        
        # Check for GPS data (presence might indicate authenticity)
        has_gps = (metadata.get("gps_latitude") != "N/A" and 
                   metadata.get("gps_longitude") != "N/A")
        
        if has_gps:
            score += 5  # Bonus for GPS data presence
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        
        return {
            "consistency_score": round(score, 2),
            "issues": issues,
            "warnings": warnings,
            "has_gps_data": has_gps,
            "verdict": MetadataService._get_consistency_verdict(score)
        }
    
    @staticmethod
    def _get_consistency_verdict(score: float) -> str:
        """Get verdict based on metadata consistency score"""
        if score >= 80:
            return "Metadata Consistent"
        elif score >= 50:
            return "Minor Inconsistencies"
        else:
            return "Major Inconsistencies"
    
    @staticmethod
    def detect_metadata_anomalies(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect specific metadata anomalies
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Dictionary with detected anomalies
        """
        anomalies = []
        
        # Check for future dates
        try:
            datetime_str = metadata.get("datetime_original", "")
            if datetime_str != "N/A" and ":" in datetime_str:
                # Parse EXIF datetime format: YYYY:MM:DD HH:MM:SS
                date_parts = datetime_str.replace(" ", ":").split(":")
                if len(date_parts) >= 3:
                    year = int(date_parts[0])
                    current_year = datetime.now().year
                    
                    if year > current_year:
                        anomalies.append(f"Future date detected: {year}")
                    elif year < 1990:
                        anomalies.append(f"Suspicious date: {year}")
        except:
            pass
        
        # Check for missing camera information
        if (metadata.get("camera_make") == "N/A" and 
            metadata.get("camera_model") == "N/A"):
            anomalies.append("No camera information found")
        
        # Check for resolution mismatches
        try:
            width = str(metadata.get("image_width", ""))
            height = str(metadata.get("image_height", ""))
            
            if width.isdigit() and height.isdigit():
                aspect_ratio = int(width) / int(height)
                common_ratios = [4/3, 3/2, 16/9, 1/1, 3/4, 2/3, 9/16]
                
                if not any(abs(aspect_ratio - ratio) < 0.1 for ratio in common_ratios):
                    anomalies.append(f"Unusual aspect ratio: {aspect_ratio:.2f}")
        except:
            pass
        
        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "has_anomalies": len(anomalies) > 0
        }
    
    @staticmethod
    def analyze_file_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Perform comprehensive metadata analysis
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing complete metadata analysis
        """
        try:
            # Extract metadata
            raw_metadata = MetadataService.extract_exif_data(file_path)
            key_metadata = MetadataService.extract_key_metadata(file_path)
            
            # Analyze consistency
            consistency = MetadataService.analyze_metadata_consistency(key_metadata)
            
            # Detect anomalies
            anomalies = MetadataService.detect_metadata_anomalies(key_metadata)
            
            return {
                "raw_metadata": raw_metadata,
                "key_metadata": key_metadata,
                "consistency_analysis": consistency,
                "anomaly_detection": anomalies,
                "metadata_score": consistency["consistency_score"],
                "overall_verdict": consistency["verdict"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing metadata: {str(e)}")
            return {
                "error": str(e),
                "metadata_score": 0.0,
                "overall_verdict": "Error"
            }


# Convenience functions
def extract_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Extract metadata from a file"""
    return MetadataService.extract_key_metadata(file_path)


def analyze_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Perform comprehensive metadata analysis"""
    return MetadataService.analyze_file_metadata(file_path)


def get_metadata_score(file_path: Union[str, Path]) -> float:
    """Get metadata consistency score"""
    metadata = MetadataService.extract_key_metadata(file_path)
    consistency = MetadataService.analyze_metadata_consistency(metadata)
    return consistency["consistency_score"]


# Example usage
if __name__ == "__main__":
    test_image = "sample.jpg"
    
    if Path(test_image).exists():
        analysis = analyze_metadata(test_image)
        print(f"Metadata Analysis Results:")
        print(f"  Score: {analysis['metadata_score']}")
        print(f"  Verdict: {analysis['overall_verdict']}")
        print(f"  Anomalies: {analysis['anomaly_detection']['anomaly_count']}")
