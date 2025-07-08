"""
File utilities for handling document uploads and processing.
"""

import os
import mimetypes
from typing import Optional, Tuple
from pathlib import Path

from app.core.config import get_settings


settings = get_settings()


def get_file_info(filename: str) -> Tuple[str, str]:
    """
    Get file type and MIME type from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Tuple of (file_extension, mime_type)
    """
    file_ext = Path(filename).suffix.lower()
    mime_type, _ = mimetypes.guess_type(filename)
    
    if not mime_type:
        # Default MIME types for common document formats
        mime_defaults = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        mime_type = mime_defaults.get(file_ext, 'application/octet-stream')
    
    return file_ext, mime_type


def is_allowed_file(filename: str) -> bool:
    """
    Check if file type is allowed for upload.
    
    Args:
        filename: Filename to check
        
    Returns:
        True if file type is allowed
    """
    file_ext, _ = get_file_info(filename)
    return file_ext in settings.allowed_file_types


def validate_file_size(file_size: int) -> bool:
    """
    Validate if file size is within allowed limits.
    
    Args:
        file_size: Size of file in bytes
        
    Returns:
        True if file size is valid
    """
    return 0 < file_size <= settings.max_upload_size


def ensure_upload_dir() -> str:
    """
    Ensure upload directory exists and return the path.
    
    Returns:
        Upload directory path
    """
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return str(upload_path)


def clean_filename(filename: str) -> str:
    """
    Clean filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    clean_name = filename
    
    for char in unsafe_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Limit filename length
    if len(clean_name) > 255:
        name_part = Path(clean_name).stem[:200]
        ext_part = Path(clean_name).suffix
        clean_name = f"{name_part}{ext_part}"
    
    return clean_name
