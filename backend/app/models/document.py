"""
Document model for storing document metadata and processing results.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Document(Base):
    """
    Document model for storing uploaded documents and their processing results.
    """
    __tablename__ = "documents"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # File storage information
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(50), default="local")
    markdown_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Processing status
    processing_status: Mapped[str] = mapped_column(String(50), default="pending")
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # Extracted content
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    ai_description: Mapped[Optional[str]] = mapped_column(Text)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata and analysis results
    document_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    analysis_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    
    # Processing configuration
    processing_options: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    
    # Quality metrics
    confidence_score: Mapped[Optional[float]] = mapped_column()
    ocr_confidence: Mapped[Optional[float]] = mapped_column()
    
    # User information
    user_id: Mapped[Optional[str]] = mapped_column(String(36))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, status={self.processing_status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "processing_status": self.processing_status,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "processing_error": self.processing_error,
            "extracted_text": self.extracted_text,
            "ai_description": self.ai_description,
            "ai_summary": self.ai_summary,
            "markdown_path": self.markdown_path,
            "document_metadata": self.document_metadata or {},
            "analysis_results": self.analysis_results or {},
            "confidence_score": self.confidence_score,
            "ocr_confidence": self.ocr_confidence,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_deleted": self.is_deleted
        }
