"""
Data Ingestion Layer
Handles file upload, validation, and initial processing
"""

import uuid
import shutil
from pathlib import Path
from typing import Union, Tuple, Optional
from datetime import datetime
from loguru import logger

from config.settings import settings


class IngestionService:
    """Service for ingesting files into the forensic system"""
    
    @staticmethod
    def validate_file(file_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return False, "File does not exist"
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds limit ({max_size_mb}MB)"
        
        # Check file extension
        file_ext = file_path.suffix.lower().lstrip('.')
        allowed_extensions = settings.allowed_extensions_list
        
        if file_ext not in allowed_extensions:
            return False, f"File type '.{file_ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1024)  # Try reading first 1KB
        except Exception as e:
            return False, f"File is not readable: {str(e)}"
        
        logger.info(f"File validation successful: {file_path.name}")
        return True, None
    
    @staticmethod
    def generate_file_id() -> str:
        """Generate unique file ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def ingest_file(
        source_path: Union[str, Path],
        original_filename: Optional[str] = None
    ) -> dict:
        """
        Ingest file into the system
        
        Args:
            source_path: Path to the source file
            original_filename: Original filename (if different from source)
            
        Returns:
            Dictionary with ingestion results
        """
        source_path = Path(source_path)
        
        # Validate file
        is_valid, error_message = IngestionService.validate_file(source_path)
        if not is_valid:
            logger.error(f"File validation failed: {error_message}")
            return {
                "success": False,
                "error": error_message
            }
        
        try:
            # Generate unique file ID
            file_id = IngestionService.generate_file_id()
            
            # Determine filename
            filename = original_filename or source_path.name
            
            # Create destination path
            upload_dir = Path(settings.UPLOAD_FOLDER)
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Use file_id in destination to avoid conflicts
            file_ext = source_path.suffix
            dest_filename = f"{file_id}_{filename}"
            dest_path = upload_dir / dest_filename
            
            # Copy file to upload folder
            shutil.copy2(source_path, dest_path)
            
            # Get file metadata
            file_stat = dest_path.stat()
            
            result = {
                "success": True,
                "file_id": file_id,
                "file_name": filename,
                "file_path": str(dest_path),
                "file_size": file_stat.st_size,
                "file_extension": file_ext.lstrip('.'),
                "uploaded_at": datetime.utcnow().isoformat(),
                "status": "ingested"
            }
            
            logger.info(f"File ingested successfully: {filename} (ID: {file_id})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error ingesting file: {str(e)}")
            return {
                "success": False,
                "error": f"Ingestion failed: {str(e)}"
            }
    
    @staticmethod
    def save_uploaded_file(file_data: bytes, filename: str) -> dict:
        """
        Save uploaded file from API request
        
        Args:
            file_data: File binary data
            filename: Original filename
            
        Returns:
            Dictionary with save results
        """
        try:
            # Create temp file
            temp_dir = Path(settings.TEMP_FOLDER)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_path = temp_dir / f"temp_{uuid.uuid4()}_{filename}"
            
            # Write data to temp file
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            
            # Ingest the temp file
            result = IngestionService.ingest_file(temp_path, filename)
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to save file: {str(e)}"
            }
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> dict:
        """
        Get basic file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": "File not found"}
        
        try:
            file_stat = file_path.stat()
            
            return {
                "file_name": file_path.name,
                "file_size": file_stat.st_size,
                "file_extension": file_path.suffix.lstrip('.'),
                "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "is_file": file_path.is_file(),
                "is_readable": True if file_path.stat().st_mode else False
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {"error": str(e)}


# Convenience functions
def validate_uploaded_file(file_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
    """Validate an uploaded file"""
    return IngestionService.validate_file(file_path)


def ingest_new_file(file_path: Union[str, Path]) -> dict:
    """Ingest a new file into the system"""
    return IngestionService.ingest_file(file_path)
