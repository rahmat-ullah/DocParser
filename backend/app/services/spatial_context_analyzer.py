"""
Spatial Context Analyzer - Maps spatial relationships within documents
to understand context and meaning more effectively.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import math

from ..parsers.ast_models import DocumentAST, TextBlock, ImageBlock, TableBlock, BlockType


logger = logging.getLogger(__name__)


class SpatialRelationship(Enum):
    """Types of spatial relationships between elements."""
    ABOVE = "above"
    BELOW = "below"
    LEFT = "left"
    RIGHT = "right"
    INSIDE = "inside"
    CONTAINS = "contains"
    ADJACENT = "adjacent"
    OVERLAPPING = "overlapping"
    SAME_COLUMN = "same_column"
    SAME_ROW = "same_row"
    NEAR = "near"
    FAR = "far"


class ElementType(Enum):
    """Types of document elements for spatial analysis."""
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    CODE = "code"
    QUOTE = "quote"
    MATH = "math"


@dataclass
class BoundingBox:
    """Represents a bounding box for spatial calculations."""
    x0: float
    y0: float
    x1: float
    y1: float
    page: int
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2
    
    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    def distance_to(self, other: 'BoundingBox') -> float:
        """Calculate distance between centers of two bounding boxes."""
        dx = self.center_x - other.center_x
        dy = self.center_y - other.center_y
        return math.sqrt(dx * dx + dy * dy)
    
    def overlaps_with(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box overlaps with another."""
        return (self.x0 < other.x1 and self.x1 > other.x0 and
                self.y0 < other.y1 and self.y1 > other.y0 and
                self.page == other.page)
    
    def contains(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box contains another."""
        return (self.x0 <= other.x0 and self.x1 >= other.x1 and
                self.y0 <= other.y0 and self.y1 >= other.y1 and
                self.page == other.page)


@dataclass
class DocumentElement:
    """Represents a document element with spatial and semantic information."""
    id: str
    type: ElementType
    bbox: BoundingBox
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    semantic_role: Optional[str] = None
    confidence: float = 1.0


@dataclass
class SpatialRelation:
    """Represents a spatial relationship between two document elements."""
    source_id: str
    target_id: str
    relationship: SpatialRelationship
    confidence: float
    distance: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentLayout:
    """Represents the spatial layout of a document."""
    elements: Dict[str, DocumentElement]
    relationships: List[SpatialRelation]
    page_dimensions: Dict[int, Tuple[float, float]]  # page -> (width, height)
    columns: Dict[int, List[Tuple[float, float]]]  # page -> [(x0, x1), ...]
    regions: Dict[str, List[str]]  # region_type -> [element_ids]


class SpatialContextAnalyzer:
    """Analyzes spatial relationships and context in documents."""
    
    def __init__(self):
        self.distance_threshold = 50.0  # pixels
        self.column_threshold = 20.0  # pixels for column detection
        self.heading_association_threshold = 100.0  # pixels
    
    def analyze_document_layout(self, ast: DocumentAST) -> DocumentLayout:
        """
        Analyze the spatial layout of a document.
        
        Args:
            ast: Document AST with spatial information
            
        Returns:
            DocumentLayout with spatial relationships
        """
        logger.info("Starting spatial context analysis")
        
        # Extract elements with spatial information
        elements = self._extract_elements(ast)
        
        # Detect page dimensions and structure
        page_dimensions = self._detect_page_dimensions(elements)
        columns = self._detect_columns(elements, page_dimensions)
        
        # Analyze spatial relationships
        relationships = self._analyze_relationships(elements)
        
        # Detect regions and semantic groupings
        regions = self._detect_regions(elements, relationships)
        
        layout = DocumentLayout(
            elements=elements,
            relationships=relationships,
            page_dimensions=page_dimensions,
            columns=columns,
            regions=regions
        )
        
        logger.info(f"Spatial analysis complete: {len(elements)} elements, {len(relationships)} relationships")
        return layout
    
    def _extract_elements(self, ast: DocumentAST) -> Dict[str, DocumentElement]:
        """Extract document elements with spatial information."""
        elements = {}
        
        # Process text blocks
        for i, text_block in enumerate(ast.textBlocks):
            if text_block.bbox:
                element_id = f"text_{i}"
                element_type = self._get_element_type(text_block.type)
                bbox = BoundingBox(
                    x0=text_block.bbox.get('x0', 0),
                    y0=text_block.bbox.get('y0', 0),
                    x1=text_block.bbox.get('x1', 0),
                    y1=text_block.bbox.get('y1', 0),
                    page=text_block.bbox.get('page', 0)
                )
                
                elements[element_id] = DocumentElement(
                    id=element_id,
                    type=element_type,
                    bbox=bbox,
                    content=text_block.content,
                    metadata={
                        'level': text_block.level,
                        'style': text_block.style,
                        'block_type': text_block.type.value if hasattr(text_block.type, 'value') else str(text_block.type)
                    }
                )
        
        # Process images
        for i, image_block in enumerate(ast.images):
            if image_block.bbox:
                element_id = f"image_{i}"
                bbox = BoundingBox(
                    x0=image_block.bbox.get('x0', 0),
                    y0=image_block.bbox.get('y0', 0),
                    x1=image_block.bbox.get('x1', 0),
                    y1=image_block.bbox.get('y1', 0),
                    page=image_block.bbox.get('page', 0)
                )
                
                elements[element_id] = DocumentElement(
                    id=element_id,
                    type=ElementType.IMAGE,
                    bbox=bbox,
                    content=image_block.alt_text or "",
                    metadata={
                        'format': image_block.format,
                        'caption': image_block.caption,
                        'metadata': getattr(image_block, 'metadata', {})
                    }
                )
        
        # Process tables
        for i, table_block in enumerate(ast.tables):
            if table_block.bbox:
                element_id = f"table_{i}"
                bbox = BoundingBox(
                    x0=table_block.bbox.get('x0', 0),
                    y0=table_block.bbox.get('y0', 0),
                    x1=table_block.bbox.get('x1', 0),
                    y1=table_block.bbox.get('y1', 0),
                    page=table_block.bbox.get('page', 0)
                )
                
                elements[element_id] = DocumentElement(
                    id=element_id,
                    type=ElementType.TABLE,
                    bbox=bbox,
                    content=f"Table with {len(table_block.headers)} columns, {len(table_block.rows)} rows",
                    metadata={
                        'headers': table_block.headers,
                        'rows': table_block.rows,
                        'caption': table_block.caption
                    }
                )
        
        return elements
    
    def _get_element_type(self, block_type: BlockType) -> ElementType:
        """Map block type to element type."""
        mapping = {
            BlockType.HEADING: ElementType.HEADING,
            BlockType.PARAGRAPH: ElementType.PARAGRAPH,
            BlockType.LIST_ITEM: ElementType.LIST_ITEM,
            BlockType.CODE: ElementType.CODE,
            BlockType.QUOTE: ElementType.QUOTE,
        }
        return mapping.get(block_type, ElementType.TEXT)
    
    def _detect_page_dimensions(self, elements: Dict[str, DocumentElement]) -> Dict[int, Tuple[float, float]]:
        """Detect page dimensions from element positions."""
        page_dims = {}
        
        for element in elements.values():
            page = element.bbox.page
            if page not in page_dims:
                page_dims[page] = (0, 0)
            
            # Update page dimensions based on element positions
            current_width, current_height = page_dims[page]
            page_dims[page] = (
                max(current_width, element.bbox.x1),
                max(current_height, element.bbox.y1)
            )
        
        return page_dims
    
    def _detect_columns(self, elements: Dict[str, DocumentElement], 
                       page_dimensions: Dict[int, Tuple[float, float]]) -> Dict[int, List[Tuple[float, float]]]:
        """Detect column structure in the document."""
        columns = {}
        
        for page, (width, height) in page_dimensions.items():
            page_elements = [e for e in elements.values() if e.bbox.page == page]
            
            if not page_elements:
                columns[page] = [(0, width)]
                continue
            
            # Group elements by their x-position
            x_positions = []
            for element in page_elements:
                x_positions.extend([element.bbox.x0, element.bbox.x1])
            
            x_positions.sort()
            
            # Find column boundaries
            column_boundaries = [0]
            for i in range(1, len(x_positions)):
                if x_positions[i] - x_positions[i-1] > self.column_threshold:
                    column_boundaries.append(x_positions[i-1])
                    column_boundaries.append(x_positions[i])
            column_boundaries.append(width)
            
            # Create column ranges
            page_columns = []
            for i in range(0, len(column_boundaries) - 1, 2):
                page_columns.append((column_boundaries[i], column_boundaries[i + 1]))
            
            columns[page] = page_columns if page_columns else [(0, width)]
        
        return columns
    
    def _analyze_relationships(self, elements: Dict[str, DocumentElement]) -> List[SpatialRelation]:
        """Analyze spatial relationships between elements."""
        relationships = []
        
        element_list = list(elements.values())
        
        for i, source in enumerate(element_list):
            for j, target in enumerate(element_list):
                if i == j or source.bbox.page != target.bbox.page:
                    continue
                
                # Calculate relationships
                relations = self._calculate_relationships(source, target)
                relationships.extend(relations)
        
        return relationships
    
    def _calculate_relationships(self, source: DocumentElement, target: DocumentElement) -> List[SpatialRelation]:
        """Calculate spatial relationships between two elements."""
        relationships = []
        distance = source.bbox.distance_to(target.bbox)
        
        # Containment relationships
        if source.bbox.contains(target.bbox):
            relationships.append(SpatialRelation(
                source_id=source.id,
                target_id=target.id,
                relationship=SpatialRelationship.CONTAINS,
                confidence=0.9,
                distance=0
            ))
        elif target.bbox.contains(source.bbox):
            relationships.append(SpatialRelation(
                source_id=source.id,
                target_id=target.id,
                relationship=SpatialRelationship.INSIDE,
                confidence=0.9,
                distance=0
            ))
        
        # Overlap relationships
        elif source.bbox.overlaps_with(target.bbox):
            relationships.append(SpatialRelation(
                source_id=source.id,
                target_id=target.id,
                relationship=SpatialRelationship.OVERLAPPING,
                confidence=0.8,
                distance=distance
            ))
        
        # Proximity relationships
        elif distance < self.distance_threshold:
            # Determine direction
            dx = target.bbox.center_x - source.bbox.center_x
            dy = target.bbox.center_y - source.bbox.center_y
            
            if abs(dx) > abs(dy):
                rel = SpatialRelationship.RIGHT if dx > 0 else SpatialRelationship.LEFT
            else:
                rel = SpatialRelationship.BELOW if dy > 0 else SpatialRelationship.ABOVE
            
            relationships.append(SpatialRelation(
                source_id=source.id,
                target_id=target.id,
                relationship=rel,
                confidence=0.7,
                distance=distance
            ))
        
        # Column relationships
        if abs(source.bbox.center_x - target.bbox.center_x) < self.column_threshold:
            relationships.append(SpatialRelation(
                source_id=source.id,
                target_id=target.id,
                relationship=SpatialRelationship.SAME_COLUMN,
                confidence=0.6,
                distance=distance
            ))
        
        # Row relationships
        if abs(source.bbox.center_y - target.bbox.center_y) < self.column_threshold:
            relationships.append(SpatialRelation(
                source_id=source.id,
                target_id=target.id,
                relationship=SpatialRelationship.SAME_ROW,
                confidence=0.6,
                distance=distance
            ))
        
        return relationships
    
    def _detect_regions(self, elements: Dict[str, DocumentElement], 
                       relationships: List[SpatialRelation]) -> Dict[str, List[str]]:
        """Detect semantic regions in the document."""
        regions = {
            'headers': [],
            'content': [],
            'figures': [],
            'tables': [],
            'captions': [],
            'footnotes': []
        }
        
        for element in elements.values():
            if element.type == ElementType.HEADING:
                regions['headers'].append(element.id)
            elif element.type == ElementType.IMAGE:
                regions['figures'].append(element.id)
            elif element.type == ElementType.TABLE:
                regions['tables'].append(element.id)
            elif element.type in [ElementType.PARAGRAPH, ElementType.TEXT]:
                # Determine if it's a caption or regular content
                if self._is_caption(element, elements, relationships):
                    regions['captions'].append(element.id)
                elif self._is_footnote(element, elements):
                    regions['footnotes'].append(element.id)
                else:
                    regions['content'].append(element.id)
        
        return regions
    
    def _is_caption(self, element: DocumentElement, elements: Dict[str, DocumentElement], 
                   relationships: List[SpatialRelation]) -> bool:
        """Determine if an element is likely a caption."""
        # Check if element is near an image or table
        for rel in relationships:
            if rel.source_id == element.id and rel.relationship in [SpatialRelationship.BELOW, SpatialRelationship.ABOVE]:
                target = elements.get(rel.target_id)
                if target and target.type in [ElementType.IMAGE, ElementType.TABLE]:
                    return True
        
        # Check for caption-like content
        content_lower = element.content.lower()
        return any(keyword in content_lower for keyword in ['figure', 'table', 'chart', 'graph', 'diagram'])
    
    def _is_footnote(self, element: DocumentElement, elements: Dict[str, DocumentElement]) -> bool:
        """Determine if an element is likely a footnote."""
        # Check position (footnotes are typically at the bottom)
        page_elements = [e for e in elements.values() if e.bbox.page == element.bbox.page]
        if not page_elements:
            return False
        
        max_y = max(e.bbox.y1 for e in page_elements)
        min_y = min(e.bbox.y0 for e in page_elements)
        
        # If element is in the bottom 20% of the page
        if (max_y - element.bbox.y0) / (max_y - min_y) < 0.2:
            return True
        
        # Check for footnote markers
        content = element.content.strip()
        return content and (content[0].isdigit() or content.startswith('*'))
    
    def get_element_context(self, element_id: str, layout: DocumentLayout, 
                           radius: float = 100.0) -> Dict[str, Any]:
        """Get contextual information for an element."""
        if element_id not in layout.elements:
            return {}
        
        element = layout.elements[element_id]
        context = {
            'element': element,
            'nearby_elements': [],
            'relationships': [],
            'semantic_context': {}
        }
        
        # Find nearby elements
        for other_id, other_element in layout.elements.items():
            if other_id != element_id and other_element.bbox.page == element.bbox.page:
                distance = element.bbox.distance_to(other_element.bbox)
                if distance <= radius:
                    context['nearby_elements'].append({
                        'id': other_id,
                        'element': other_element,
                        'distance': distance
                    })
        
        # Find relationships
        for rel in layout.relationships:
            if rel.source_id == element_id or rel.target_id == element_id:
                context['relationships'].append(rel)
        
        # Determine semantic context
        context['semantic_context'] = self._analyze_semantic_context(element, layout)
        
        return context
    
    def _analyze_semantic_context(self, element: DocumentElement, layout: DocumentLayout) -> Dict[str, Any]:
        """Analyze semantic context of an element."""
        context = {
            'role': 'content',
            'section': None,
            'associated_elements': []
        }
        
        # Find associated heading
        for rel in layout.relationships:
            if (rel.target_id == element.id and 
                rel.relationship == SpatialRelationship.BELOW and
                rel.distance < self.heading_association_threshold):
                
                source = layout.elements.get(rel.source_id)
                if source and source.type == ElementType.HEADING:
                    context['section'] = source.content
                    break
        
        # Determine role based on type and relationships
        if element.type == ElementType.HEADING:
            context['role'] = 'section_header'
        elif element.type == ElementType.IMAGE:
            context['role'] = 'illustration'
        elif element.type == ElementType.TABLE:
            context['role'] = 'data_presentation'
        
        return context
