"""
Image and diagram metadata schemas for structured data extraction.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ImageSource(BaseModel):
    """Source information for an image/diagram."""
    filename: str = Field(..., description="Name of the source file")
    page: int = Field(..., description="Page number where the image appears")
    documentSection: str = Field(default="", description="Document section containing the image")


class ImageLocation(BaseModel):
    """Physical location coordinates of the image in the document."""
    x: float = Field(default=0, description="X coordinate")
    y: float = Field(default=0, description="Y coordinate")
    width: float = Field(default=0, description="Image width")
    height: float = Field(default=0, description="Image height")


class LinkedEntity(BaseModel):
    """Entity linked to the image content."""
    type: str = Field(..., description="Type of entity (concept, unit, component, etc.)")
    value: str = Field(..., description="Entity value")


class TextReference(BaseModel):
    """Reference to the image from document text."""
    text: str = Field(..., description="Text that references the image")
    section: str = Field(..., description="Section containing the reference")
    page: int = Field(..., description="Page number of the reference")


class AIAnnotations(BaseModel):
    """AI-generated annotations for the image."""
    objectsDetected: List[str] = Field(default_factory=list, description="Objects detected in the image")
    ocrText: str = Field(default="", description="Text extracted via OCR")
    language: str = Field(default="en", description="Language of text in the image")
    explanationGenerated: str = Field(default="", description="AI-generated explanation")


class ImageRelations(BaseModel):
    """Relationships between the image and other document elements."""
    explains: List[str] = Field(default_factory=list, description="IDs of elements this image explains")
    referencedBy: List[str] = Field(default_factory=list, description="IDs of elements that reference this image")


class ImageMetadata(BaseModel):
    """Complete metadata structure for an image or diagram."""
    id: str = Field(..., description="Unique identifier for the image")
    type: str = Field(..., description="Type of visual (image, diagram, chart, graph, etc.)")
    title: str = Field(default="", description="Title of the image")
    caption: str = Field(default="", description="Caption text")
    source: ImageSource = Field(..., description="Source information")
    location: ImageLocation = Field(default_factory=ImageLocation, description="Physical location in document")
    description: str = Field(default="", description="Brief description of the image content")
    contextualSummary: str = Field(default="", description="How the image relates to surrounding content")
    linkedEntities: List[LinkedEntity] = Field(default_factory=list, description="Entities linked to the image")
    textReferences: List[TextReference] = Field(default_factory=list, description="Text references to the image")
    semanticTags: List[str] = Field(default_factory=list, description="Semantic tags for categorization")
    aiAnnotations: AIAnnotations = Field(default_factory=AIAnnotations, description="AI-generated annotations")
    relations: ImageRelations = Field(default_factory=ImageRelations, description="Relationships to other elements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "fig-001",
                "type": "diagram",
                "title": "Energy Flow Diagram",
                "caption": "Figure 3.1 shows energy flow between production and consumption units.",
                "source": {
                    "filename": "energy_report.pdf",
                    "page": 12,
                    "documentSection": "Chapter 3: Methodology"
                },
                "location": {
                    "x": 120,
                    "y": 330,
                    "width": 480,
                    "height": 320
                },
                "description": "A Sankey diagram showing how energy is lost or consumed through different units in the power grid.",
                "contextualSummary": "This figure supports the discussion on grid efficiency and transmission losses.",
                "linkedEntities": [
                    {"type": "concept", "value": "Energy Loss"},
                    {"type": "unit", "value": "MW"},
                    {"type": "component", "value": "Transformer"}
                ],
                "textReferences": [
                    {
                        "text": "As shown in Figure 3.1, a large portion of energy is lost in transmission.",
                        "section": "3.2 Transmission Efficiency",
                        "page": 13
                    }
                ],
                "semanticTags": ["energy", "Sankey", "efficiency", "visual-explanation"],
                "aiAnnotations": {
                    "objectsDetected": ["transformer", "transmission line", "battery"],
                    "ocrText": "INPUT 500 MW → OUTPUT 300 MW → LOSS 200 MW",
                    "language": "en",
                    "explanationGenerated": "The diagram visualizes how 500 MW of input results in 200 MW of transmission losses."
                },
                "relations": {
                    "explains": ["paragraph-3.1"],
                    "referencedBy": ["section-3.2", "conclusion"]
                }
            }
        }


class ImageMetadataList(BaseModel):
    """List of image metadata for a document."""
    images: List[ImageMetadata] = Field(..., description="List of image metadata")
    documentId: str = Field(..., description="ID of the parent document")
    totalImages: int = Field(..., description="Total number of images in the document")
