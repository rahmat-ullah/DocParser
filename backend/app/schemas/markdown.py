"""
Markdown-related schemas for document markdown path operations.
"""

from typing import Optional

from pydantic import BaseModel, Field


class MarkdownPathUpdate(BaseModel):
    """
    Schema for updating document's markdown path.
    """
    markdown_path: str = Field(..., example="/uploads/markdown/document-123.md")


class MarkdownPathResponse(BaseModel):
    """
    Schema for markdown path response.
    """
    document_id: str
    markdown_path: Optional[str] = None
    
    class Config:
        from_attributes = True
