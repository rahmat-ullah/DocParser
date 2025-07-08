"""
Document schemas for API request and response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """
    Schema for creating a new document.
    """
    filename: str = Field(..., example="document.pdf")
    content: str = Field(..., example="Base64 encoded content here")


class DocumentUpdate(BaseModel):
    """
    Schema for updating a document's metadata or status.
    """
    processing_status: Optional[str] = Field(example="completed")
    ai_summary: Optional[str]
    ai_description: Optional[str]


class DocumentResponse(BaseModel):
    """
    Schema for detailed document information response.
    """
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    processing_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    extracted_text: Optional[str] = None
    ai_description: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """
    Schema for listing documents.
    """
    documents: List[DocumentResponse]


class ProcessingRequest(BaseModel):
    """
    Schema for processing request for a document.
    """
    processing_options: Optional[Dict[str, Any]] = Field(default_factory=dict, example={"use_ai": True, "priority": 1})


class ProcessingResponse(BaseModel):
    """
    Schema for processing response with operation outcome.
    """
    success: bool
    message: str
