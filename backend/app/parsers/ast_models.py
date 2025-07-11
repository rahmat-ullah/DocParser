"""
AST (Abstract Syntax Tree) models for document parsing.
Defines the standard structure that all parsers should return.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class BlockType(str, Enum):
    """Types of text blocks."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    QUOTE = "quote"
    CODE = "code"


class TextBlock(BaseModel):
    """Represents a block of text content."""
    type: BlockType
    content: str
    level: Optional[int] = None  # For headings, list nesting
    style: Dict[str, Any] = Field(default_factory=dict)  # Font, size, color, etc.
    bbox: Optional[Dict[str, float]] = None  # Bounding box coordinates


class ImageBlock(BaseModel):
    """Represents an image within the document."""
    data: str  # Base64 encoded image data
    format: str  # PNG, JPEG, etc.
    bbox: Optional[Dict[str, float]] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # Structured metadata from AI analysis
    source: Optional[str] = None  # Source document filename
    page: Optional[int] = None  # Page number in document
    section: Optional[str] = None  # Document section
    index: Optional[int] = None  # Image index in document


class TableBlock(BaseModel):
    """Represents a table structure."""
    headers: List[str]
    rows: List[List[str]]
    bbox: Optional[Dict[str, float]] = None
    caption: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)


class MathBlock(BaseModel):
    """Represents mathematical content."""
    content: str  # LaTeX or MathML format
    format: str = "latex"  # latex, mathml, text
    is_inline: bool = False
    bbox: Optional[Dict[str, float]] = None


class DocumentAST(BaseModel):
    """
    Abstract Syntax Tree for parsed documents.
    This is the standard structure returned by all parsers.
    """
    textBlocks: List[TextBlock] = Field(default_factory=list)
    images: List[ImageBlock] = Field(default_factory=list)
    tables: List[TableBlock] = Field(default_factory=list)
    math: List[MathBlock] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Title, author, created_date, etc.


class ParseProgress(BaseModel):
    """Progress information for parsing operations."""
    stage: str
    progress: float  # 0.0 to 1.0
    message: str
    details: Optional[Dict[str, Any]] = None
    result: Optional[str] = None  # Final result content (e.g., markdown)
