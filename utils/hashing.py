"""
SHA-256 Hashing Utilities
Provides file integrity verification through cryptographic hashing
"""

import hashlib
from pathlib import Path
from typing import Union, Optional
from loguru import logger


class HashingService:
    """Service for generating and verifying SHA-256 hashes"""
    
    CHUNK_SIZE = 8192  # Read files in 8KB chunks
    
    @staticmethod
    def calculate_sha256(file_path: Union[str, Path]) -> str:
        """
        Calculate SHA-256 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal representation of SHA-256 hash
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(HashingService.CHUNK_SIZE), b""):
                    sha256_hash.update(chunk)
            
            hash_value = sha256_hash.hexdigest()
            logger.info(f"Calculated SHA-256 for {file_path.name}: {hash_value[:16]}...")
            return hash_value
            
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def calculate_string_hash(content: str) -> str:
        """
        Calculate SHA-256 hash of a string
        
        Args:
            content: String content to hash
            
        Returns:
            Hexadecimal representation of SHA-256 hash
        """
        sha256_hash = hashlib.sha256(content.encode('utf-8'))
        return sha256_hash.hexdigest()
    
    @staticmethod
    def verify_integrity(file_path: Union[str, Path], expected_hash: str) -> bool:
        """
        Verify file integrity by comparing hash with expected value
        
        Args:
            file_path: Path to the file
            expected_hash: Expected SHA-256 hash value
            
        Returns:
            True if hashes match, False otherwise
        """
        try:
            actual_hash = HashingService.calculate_sha256(file_path)
            match = actual_hash.lower() == expected_hash.lower()
            
            if match:
                logger.info(f"Hash verification successful for {Path(file_path).name}")
            else:
                logger.warning(f"Hash mismatch for {Path(file_path).name}")
                logger.debug(f"Expected: {expected_hash}")
                logger.debug(f"Actual: {actual_hash}")
            
            return match
            
        except Exception as e:
            logger.error(f"Error verifying hash: {str(e)}")
            return False
    
    @staticmethod
    def calculate_score(file_path: Union[str, Path], original_hash: Optional[str] = None) -> float:
        """
        Calculate hash-based authenticity score
        
        Args:
            file_path: Path to the file
            original_hash: Original hash to compare against (optional)
            
        Returns:
            Score from 0-100 (100 = perfect match, 0 = no match or error)
        """
        if original_hash is None:
            # If no original hash provided, just verify we can calculate hash
            try:
                HashingService.calculate_sha256(file_path)
                return 100.0  # File can be hashed successfully
            except Exception as e:
                logger.error(f"Hash calculation failed: {str(e)}")
                return 0.0
        else:
            # Verify against original hash
            return 100.0 if HashingService.verify_integrity(file_path, original_hash) else 0.0
    
    @staticmethod
    def generate_file_signature(file_path: Union[str, Path]) -> dict:
        """
        Generate comprehensive file signature
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing hash and metadata
        """
        file_path = Path(file_path)
        
        try:
            hash_value = HashingService.calculate_sha256(file_path)
            file_stat = file_path.stat()
            
            return {
                "sha256": hash_value,
                "file_size": file_stat.st_size,
                "file_name": file_path.name,
                "md5": HashingService._calculate_md5(file_path),  # Additional hash for comparison
            }
            
        except Exception as e:
            logger.error(f"Error generating file signature: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_md5(file_path: Path) -> str:
        """Calculate MD5 hash (for additional verification)"""
        md5_hash = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(HashingService.CHUNK_SIZE), b""):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()


# Convenience functions for direct use
def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """Calculate SHA-256 hash of a file"""
    return HashingService.calculate_sha256(file_path)


def verify_file_integrity(file_path: Union[str, Path], expected_hash: str) -> bool:
    """Verify file integrity"""
    return HashingService.verify_integrity(file_path, expected_hash)


def get_file_signature(file_path: Union[str, Path]) -> dict:
    """Get comprehensive file signature"""
    return HashingService.generate_file_signature(file_path)


# Example usage
if __name__ == "__main__":
    # Example: Calculate hash for a file
    test_file = "sample.jpg"
    
    if Path(test_file).exists():
        hash_value = calculate_file_hash(test_file)
        print(f"SHA-256: {hash_value}")
        
        signature = get_file_signature(test_file)
        print(f"File Signature: {signature}")
