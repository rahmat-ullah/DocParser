"""
AST (Abstract Syntax Tree) models for document parsing.
Defines the standard structure that all parsers should return.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4


class BlockType(str, Enum):
    """Types of text blocks."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    QUOTE = "quote"
    CODE = "code"
    SECTION = "section"
    FOOTNOTE = "footnote"
    CAPTION = "caption"
    ANNOTATION = "annotation"


class HierarchicalNode(BaseModel):
    """Base class for hierarchical document elements."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    order: int = 0  # Order within parent
    bbox: Optional[Dict[str, float]] = None  # Bounding box coordinates
    metadata: Dict[str, Any] = Field(default_factory=dict)
    spatial_context: Optional[Dict[str, Any]] = None


class TextBlock(HierarchicalNode):
    """Represents a block of text content."""
    type: BlockType
    content: str
    level: Optional[int] = None  # For headings, list nesting
    style: Dict[str, Any] = Field(default_factory=dict)  # Font, size, color, etc.
    # Inherited: id, parent_id, children_ids, order, bbox, metadata


class ImageBlock(HierarchicalNode):
    """Represents an image within the document."""
    data: str  # Base64 encoded image data
    format: str  # PNG, JPEG, etc.
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    source: Optional[str] = None  # Source document filename
    page: Optional[int] = None  # Page number in document
    section: Optional[str] = None  # Document section
    index: Optional[int] = None  # Image index in document
    # Inherited: id, parent_id, children_ids, order, bbox, metadata


class TableBlock(HierarchicalNode):
    """Represents a table structure."""
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    # Inherited: id, parent_id, children_ids, order, bbox, metadata


class MathBlock(HierarchicalNode):
    """Represents mathematical content."""
    content: str  # LaTeX or MathML format
    format: str = "latex"  # latex, mathml, text
    is_inline: bool = False
    # Inherited: id, parent_id, children_ids, order, bbox, metadata

class DocumentSection(HierarchicalNode):
    """Represents a logical section of the document."""
    title: Optional[str] = None
    section_type: str = "section"  # section, chapter, appendix, etc.
    level: int = 0  # Nesting level

# Union type for all possible document elements
DocumentElement = Union[TextBlock, ImageBlock, TableBlock, MathBlock, DocumentSection]

    

class DocumentAST(BaseModel):
    """
    Hierarchical Abstract Syntax Tree for parsed documents.
    This is the standard structure returned by all parsers.
    """
    # Flat lists for backward compatibility
    textBlocks: List[TextBlock] = Field(default_factory=list)
    images: List[ImageBlock] = Field(default_factory=list)
    tables: List[TableBlock] = Field(default_factory=list)
    math: List[MathBlock] = Field(default_factory=list)
    sections: List[DocumentSection] = Field(default_factory=list)
    
    # Hierarchical structure
    elements: Dict[str, DocumentElement] = Field(default_factory=dict)  # id -> element mapping
    root_elements: List[str] = Field(default_factory=list)  # Root element IDs
    
    # Document metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Title, author, created_date, etc.
    
    def add_element(self, element: DocumentElement, parent_id: Optional[str] = None) -> str:
        """Add an element to the AST and establish parent-child relationships."""
        # Add to elements dictionary
        self.elements[element.id] = element
        
        # Set parent-child relationships
        if parent_id:
            element.parent_id = parent_id
            if parent_id in self.elements:
                self.elements[parent_id].children_ids.append(element.id)
        else:
            # Root element
            self.root_elements.append(element.id)
        
        # Add to legacy flat lists for backward compatibility
        if isinstance(element, TextBlock):
            self.textBlocks.append(element)
        elif isinstance(element, ImageBlock):
            self.images.append(element)
        elif isinstance(element, TableBlock):
            self.tables.append(element)
        elif isinstance(element, MathBlock):
            self.math.append(element)
        
        return element.id
    
    def get_children(self, element_id: str) -> List[DocumentElement]:
        """Get all direct children of an element."""
        if element_id not in self.elements:
            return []
        
        element = self.elements[element_id]
        return [self.elements[child_id] for child_id in element.children_ids if child_id in self.elements]
    
    def get_descendants(self, element_id: str) -> List[DocumentElement]:
        """Get all descendants (children, grandchildren, etc.) of an element."""
        descendants = []
        children = self.get_children(element_id)
        
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_descendants(child.id))
        
        return descendants
    
    def get_parent(self, element_id: str) -> Optional[DocumentElement]:
        """Get the parent element of an element."""
        if element_id not in self.elements:
            return None
        
        element = self.elements[element_id]
        if element.parent_id and element.parent_id in self.elements:
            return self.elements[element.parent_id]
        
        return None
    
    def get_siblings(self, element_id: str) -> List[DocumentElement]:
        """Get all sibling elements of an element."""
        parent = self.get_parent(element_id)
        if parent:
            return [child for child in self.get_children(parent.id) if child.id != element_id]
        else:
            # Root level siblings
            return [self.elements[root_id] for root_id in self.root_elements if root_id != element_id]
    
    def get_element_path(self, element_id: str) -> List[str]:
        """Get the path from root to element as a list of element IDs."""
        path = []
        current_id = element_id
        
        while current_id:
            path.insert(0, current_id)
            parent = self.get_parent(current_id)
            current_id = parent.id if parent else None
        
        return path
    
    def reorganize_hierarchy(self) -> None:
        """Reorganize flat elements into hierarchical structure based on document structure."""
        # Sort text blocks by position and heading levels
        sorted_text_blocks = sorted(self.textBlocks, key=lambda x: (x.order, x.level or 0))
        
        current_section = None
        current_parent = None
        
        for block in sorted_text_blocks:
            if block.type == BlockType.HEADING:
                # Create new section for headings
                section = DocumentSection(
                    title=block.content,
                    level=block.level or 0,
                    bbox=block.bbox,
                    order=block.order
                )
                
                # Determine parent based on heading level
                if block.level == 1 or current_section is None:
                    # Top-level heading
                    section.parent_id = None
                    current_section = section
                else:
                    # Nested heading - find appropriate parent
                    section.parent_id = current_section.id if current_section else None
                
                self.sections.append(section)
                self.add_element(section)
                current_parent = section.id
                
            elif current_parent:
                # Add block to current section
                block.parent_id = current_parent
                if current_parent in self.elements:
                    self.elements[current_parent].children_ids.append(block.id)


class ParseProgress(BaseModel):
    """Progress information for parsing operations."""
    stage: str
    progress: float  # 0.0 to 1.0
    message: str
    details: Optional[Dict[str, Any]] = None
    result: Optional[str] = None  # Final result content (e.g., markdown)
