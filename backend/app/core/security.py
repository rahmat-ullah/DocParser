"""
Security utilities for the Document Parser application.
Provides functions for sanitization and validation.
"""

import os
import re
from typing import List


def sanitize_filename(filename: str) -> str:
    """
    Sanitize the input filename to ensure it is safe for use in file systems.

    Args:
        filename (str): The filename to sanitize.

    Returns:
        str: The sanitized filename.
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?"<>|]', '_', filename)

    # Remove leading and trailing spaces
    sanitized = sanitized.strip()

    # Ensure filename is not empty
    if not sanitized:
        raise ValueError("Filename cannot be empty after sanitization.")

    return sanitized


def is_content_type_allowed(content_type: str, allowed_types: List[str]) -> bool:
    """
    Check if the provided content type is in the list of allowed types.

    Args:
        content_type (str): The content type to check.
        allowed_types (List[str]): List of allowed content types.

    Returns:
        bool: True if the content type is allowed, False otherwise.
    """
    return content_type.lower() in map(str.lower, allowed_types)


def is_size_within_limit(size: int, max_size: int) -> bool:
    """
    Check if the provided size is within the allowed limit.

    Args:
        size (int): The size in bytes to check.
        max_size (int): The maximum allowed size in bytes.

    Returns:
        bool: True if the size is within the limit, False otherwise.
    """
    return size <= max_size

