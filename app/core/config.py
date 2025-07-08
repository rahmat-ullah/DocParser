"""
Configuration module for the Document Parser application.
Handles loading environment variables and application settings.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="Document Parser", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for sessions")
    
    # OpenAI settings
    openai_api_key: str = Field(default="", description="OpenAI API key for document processing")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")
    openai_vision_model: str = Field(default="gpt-4-vision-preview", description="OpenAI Vision model to use")
    openai_max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    openai_retry_delay: float = Field(default=1.0, description="Initial retry delay in seconds")
    openai_timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # OCR settings
    ocr_fallback_enabled: bool = Field(default=True, description="Enable OCR fallback when Vision API fails")
    tesseract_path: Optional[str] = Field(default=None, description="Path to Tesseract executable")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"], 
        description="Allowed CORS origins"
    )
    
    # Upload settings
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="Maximum upload size in bytes (10MB)")
    max_files_per_upload: int = Field(default=5, description="Maximum number of files per upload")
    allowed_file_types: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".md", ".doc"],
        description="Allowed file extensions"
    )
    
    # Directory settings
    temp_dir: str = Field(default="./temp", description="Temporary directory for file processing")
    upload_dir: str = Field(default="./uploads", description="Directory for uploaded files")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./docparser.db", description="Database URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_file_types', pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',')]
        return v
    
    @validator('temp_dir', 'upload_dir', pre=True)
    def create_directories(cls, v):
        """Ensure directories exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @validator('log_file', pre=True)
    def create_log_directory(cls, v):
        """Ensure log directory exists."""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)
    
    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if v and not v.startswith(('sk-', 'sk-proj-')):
            raise ValueError("OpenAI API key must start with 'sk-' or 'sk-proj-'")
        return v
    
    @validator('max_upload_size')
    def validate_upload_size(cls, v):
        """Validate upload size is reasonable."""
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError("Maximum upload size cannot exceed 100MB")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable prefixes
        env_prefix = ""
        
        # Field mappings for environment variables
        fields = {
            'openai_api_key': {'env': 'OPENAI_API_KEY'},
            'cors_origins': {'env': 'CORS_ORIGINS'},
            'max_upload_size': {'env': 'MAX_UPLOAD_SIZE'},
            'temp_dir': {'env': 'TEMP_DIR'},
            'upload_dir': {'env': 'UPLOAD_DIR'},
            'log_level': {'env': 'LOG_LEVEL'},
            'log_file': {'env': 'LOG_FILE'},
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global settings
    settings = Settings()
    return settings


# Utility functions for common configuration access
def get_openai_config() -> dict:
    """Get OpenAI configuration."""
    return {
        "api_key": settings.openai_api_key,
        "model": settings.openai_model,
        "vision_model": settings.openai_vision_model,
        "max_retries": settings.openai_max_retries,
        "retry_delay": settings.openai_retry_delay,
        "timeout": settings.openai_timeout,
        "ocr_fallback_enabled": settings.ocr_fallback_enabled,
        "tesseract_path": settings.tesseract_path,
    }


def get_cors_config() -> dict:
    """Get CORS configuration."""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
    }


def get_upload_config() -> dict:
    """Get upload configuration."""
    return {
        "max_size": settings.max_upload_size,
        "max_files": settings.max_files_per_upload,
        "allowed_types": settings.allowed_file_types,
        "temp_dir": settings.temp_dir,
        "upload_dir": settings.upload_dir,
    }


def get_database_config() -> dict:
    """Get database configuration."""
    return {
        "url": settings.database_url,
    }


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.debug


def is_production() -> bool:
    """Check if running in production mode."""
    return not settings.debug
