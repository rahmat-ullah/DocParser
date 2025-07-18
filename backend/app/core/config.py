"""
Configuration module for the Document Parser application.
Handles loading environment variables and application settings.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="Document Parser", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for sessions")
    
    # OpenAI settings
    openai_api_key: str = Field(default="", description="OpenAI API key for document processing")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use for text processing")
    openai_vision_model: str = Field(default="gpt-4o", description="OpenAI Vision model to use for image analysis")
    openai_reasoning_model: str = Field(default="o1-preview", description="OpenAI reasoning model for complex analysis")
    openai_max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    openai_retry_delay: float = Field(default=1.0, description="Initial retry delay in seconds")
    openai_timeout: int = Field(default=60, description="Request timeout in seconds")
    openai_max_tokens: int = Field(default=4000, description="Maximum tokens for OpenAI responses")
    openai_temperature: float = Field(default=0.1, description="Temperature for OpenAI responses (0.0-2.0)")
    
    # Advanced AI features
    use_structured_outputs: bool = Field(default=True, description="Use structured outputs for better parsing")
    enable_multi_modal_analysis: bool = Field(default=True, description="Enable multi-modal analysis for complex documents")
    use_reasoning_model_for_complex_docs: bool = Field(default=False, description="Use reasoning model for complex document analysis")
    enable_contextual_understanding: bool = Field(default=True, description="Enable contextual understanding across document sections")
    
    # Document type specific models
    scientific_paper_model: str = Field(default="gpt-4o", description="Model for scientific papers")
    financial_report_model: str = Field(default="gpt-4o", description="Model for financial reports")
    technical_manual_model: str = Field(default="gpt-4o", description="Model for technical manuals")
    legal_document_model: str = Field(default="gpt-4o", description="Model for legal documents")
    
    # OCR settings
    ocr_fallback_enabled: bool = Field(default=True, description="Enable OCR fallback when Vision API fails")
    tesseract_path: Optional[str] = Field(default=None, description="Path to Tesseract executable")
    extract_tables_from_images_enabled: bool = Field(default=True, description="Enable table extraction from images using OCR+LLM")
    # extract_tables_from_images_enabled: bool = Field(default=True, description="Enable table extraction from images using OCR+LLM (can be slow)")
    ai_processor_image_batch_size: int = Field(default=3, description="Batch size for concurrent image processing in AIProcessor")
    
    # Advanced table extraction settings
    enable_advanced_table_extraction: bool = Field(default=True, description="Enable advanced table extraction using Camelot, pdfplumber, and GMFT")
    table_extraction_quality_threshold: float = Field(default=0.3, description="Minimum confidence score for table extraction")
    table_extraction_iou_threshold: float = Field(default=0.6, description="IoU threshold for table deduplication")
    table_extraction_max_empty_cell_ratio: float = Field(default=0.7, description="Maximum ratio of empty cells in extracted tables")
    table_extraction_min_rows: int = Field(default=2, description="Minimum number of rows for valid tables")
    table_extraction_min_columns: int = Field(default=2, description="Minimum number of columns for valid tables")
    camelot_lattice_enabled: bool = Field(default=True, description="Enable Camelot lattice flavor for table extraction")
    camelot_stream_enabled: bool = Field(default=True, description="Enable Camelot stream flavor for table extraction")
    gmft_enabled: bool = Field(default=True, description="Enable GMFT (deep learning) table extraction")
    gmft_detection_threshold: float = Field(default=0.5, description="GMFT detection confidence threshold")
    pdfplumber_repair_enabled: bool = Field(default=True, description="Enable pdfplumber text repair for tables")
    
    # CORS settings
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001", 
        description="Allowed CORS origins (comma-separated)"
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
    markdown_dir: str = Field(default="./markdown", description="Directory for generated markdown files")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./docparser.db", description="Database URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return v.strip()
        return v
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return self.cors_origins
    
    @field_validator('allowed_file_types', mode='before')
    @classmethod
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',')]
        return v
    
    @field_validator('temp_dir', 'upload_dir', 'markdown_dir', mode='before')
    @classmethod
    def create_directories(cls, v):
        """Ensure directories exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @field_validator('log_file', mode='before')
    @classmethod
    def create_log_directory(cls, v):
        """Ensure log directory exists."""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if v and v != "your_openai_api_key_here" and not v.startswith(('sk-', 'sk-proj-')):
            raise ValueError("OpenAI API key must start with 'sk-' or 'sk-proj-'")
        return v
    
    @field_validator('max_upload_size')
    @classmethod
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
        "reasoning_model": settings.openai_reasoning_model,
        "max_retries": settings.openai_max_retries,
        "retry_delay": settings.openai_retry_delay,
        "timeout": settings.openai_timeout,
        "max_tokens": settings.openai_max_tokens,
        "temperature": settings.openai_temperature,
        "use_structured_outputs": settings.use_structured_outputs,
        "enable_multi_modal_analysis": settings.enable_multi_modal_analysis,
        "use_reasoning_model_for_complex_docs": settings.use_reasoning_model_for_complex_docs,
        "enable_contextual_understanding": settings.enable_contextual_understanding,
        "ocr_fallback_enabled": settings.ocr_fallback_enabled,
        "tesseract_path": settings.tesseract_path,
        "document_type_models": {
            "scientific_paper": settings.scientific_paper_model,
            "financial_report": settings.financial_report_model,
            "technical_manual": settings.technical_manual_model,
            "legal_document": settings.legal_document_model,
        },
    }


def get_cors_config() -> dict:
    """Get CORS configuration."""
    return {
        "allow_origins": settings.get_cors_origins_list(),
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
