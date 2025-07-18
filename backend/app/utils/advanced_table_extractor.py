"""
Advanced Table Extraction Module

This module implements a hybrid approach to table extraction from PDFs using:
1. Camelot (rule-based, fast for vector PDFs with lines/structure)
2. pdfplumber (text-based extraction and cell repair)
3. GMFT (deep learning Table Transformer for scanned/complex tables)

The module follows a multi-stage pipeline:
- Stage 1: Rule-based extraction (Camelot lattice/stream)
- Stage 2: Deep learning fallback (GMFT with Table Transformer)
- Stage 3: Merge, deduplicate, and canonicalize results
- Stage 4: Post-process for spans and export
"""

import asyncio
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

import pandas as pd
import numpy as np
from PIL import Image

# Table extraction libraries
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    warnings.warn("Camelot not available. Install with: pip install 'camelot-py[cv]'")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    warnings.warn("pdfplumber not available. Install with: pip install pdfplumber")

try:
    import gmft
    GMFT_AVAILABLE = True
except ImportError:
    GMFT_AVAILABLE = False
    warnings.warn("GMFT not available. Install with: pip install gmft")

from ..parsers.ast_models import TableBlock


logger = logging.getLogger(__name__)


class TableExtractionConfig:
    """Configuration for table extraction parameters."""
    
    def __init__(self):
        # Quality thresholds
        self.min_cell_length = 2
        self.min_column_count = 2
        self.min_row_count = 2
        self.max_empty_cell_ratio = 0.7
        
        # IoU threshold for deduplication
        self.iou_threshold = 0.6
        
        # Confidence scoring
        self.min_confidence_score = 0.3
        
        # GMFT settings
        self.gmft_enable_cuda = True
        self.gmft_detection_threshold = 0.5
        
        # Camelot settings
        self.camelot_lattice_threshold = 2  # min rows for lattice to be considered valid
        
        # pdfplumber settings
        self.pdfplumber_repair_enabled = True


class CanonicalTable:
    """Canonical table representation for unified processing."""
    
    def __init__(
        self,
        id: str,
        source: str,
        page: int,
        bbox: Tuple[float, float, float, float],
        cells: List[List[str]],
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.source = source
        self.page = page
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.cells = cells
        self.confidence = confidence
        self.metadata = metadata or {}
        
        # Derived properties
        self.row_count = len(cells)
        self.col_count = max(len(row) for row in cells) if cells else 0
        self.total_cells = self.row_count * self.col_count
        self.empty_cells = sum(1 for row in cells for cell in row if not cell.strip())
        self.empty_cell_ratio = self.empty_cells / self.total_cells if self.total_cells > 0 else 1.0
        
    def to_table_block(self) -> TableBlock:
        """Convert to AST TableBlock."""
        headers = self.cells[0] if self.cells else []
        rows = self.cells[1:] if len(self.cells) > 1 else []
        
        return TableBlock(
            headers=headers,
            rows=rows,
            bbox={
                "x0": self.bbox[0],
                "y0": self.bbox[1], 
                "x1": self.bbox[2],
                "y1": self.bbox[3],
                "page": self.page
            },
            metadata={
                "extraction_source": self.source,
                "confidence": self.confidence,
                "extraction_id": self.id,
                **self.metadata
            }
        )
        
    def calculate_quality_score(self) -> float:
        """Calculate a quality score for this table."""
        if self.total_cells == 0:
            return 0.0
            
        # Factors for quality scoring
        size_score = min(1.0, (self.row_count * self.col_count) / 20)  # normalize by 20 cells
        content_score = 1.0 - self.empty_cell_ratio
        structure_score = 1.0 if self.col_count >= 2 and self.row_count >= 2 else 0.5
        
        # Average cell length score
        non_empty_cells = [cell for row in self.cells for cell in row if cell.strip()]
        avg_cell_length = sum(len(cell) for cell in non_empty_cells) / len(non_empty_cells) if non_empty_cells else 0
        length_score = min(1.0, avg_cell_length / 10)  # normalize by 10 characters
        
        return (size_score * 0.3 + content_score * 0.4 + structure_score * 0.2 + length_score * 0.1)


class AdvancedTableExtractor:
    """Advanced table extraction engine using multiple approaches."""
    
    def __init__(self, config: Optional[TableExtractionConfig] = None):
        self.config = config or TableExtractionConfig()
        
    async def extract_tables(
        self, 
        pdf_path: str, 
        pages: Optional[str] = "all"
    ) -> List[CanonicalTable]:
        """
        Extract tables from PDF using hybrid approach.
        
        Args:
            pdf_path: Path to PDF file
            pages: Page specification (e.g., "all", "1", "1,2,3", "1-3")
            
        Returns:
            List of canonical tables
        """
        logger.info(f"Starting table extraction from {pdf_path}")
        
        # Stage 1: Rule-based extraction
        camelot_tables = await self._extract_with_camelot(pdf_path, pages)
        logger.info(f"Camelot extracted {len(camelot_tables)} tables")
        
        # Stage 2: Text-based repair (optional)
        if self.config.pdfplumber_repair_enabled:
            camelot_tables = await self._repair_with_pdfplumber(pdf_path, camelot_tables)
        
        # Stage 3: Deep learning fallback
        gmft_tables = await self._extract_with_gmft(pdf_path, pages)
        logger.info(f"GMFT extracted {len(gmft_tables)} tables")
        
        # Stage 4: Merge and deduplicate
        all_tables = camelot_tables + gmft_tables
        canonical_tables = self._merge_and_deduplicate(all_tables)
        logger.info(f"Final result: {len(canonical_tables)} unique tables")
        
        # Stage 5: Quality filtering
        quality_tables = self._filter_by_quality(canonical_tables)
        logger.info(f"After quality filtering: {len(quality_tables)} tables")
        
        return quality_tables
    
    async def _extract_with_camelot(
        self, 
        pdf_path: str, 
        pages: str
    ) -> List[CanonicalTable]:
        """Extract tables using Camelot (lattice and stream flavors)."""
        if not CAMELOT_AVAILABLE:
            logger.warning("Camelot not available, skipping rule-based extraction")
            return []
            
        tables = []
        
        try:
            # Try lattice flavor first (better for tables with lines)
            logger.debug("Extracting with Camelot lattice flavor")
            lattice_tables = camelot.read_pdf(pdf_path, flavor="lattice", pages=pages)
            
            # Keep lattice tables that meet quality threshold
            good_lattice_tables = [
                t for t in lattice_tables 
                if len(t.df) >= self.config.camelot_lattice_threshold
            ]
            
            if good_lattice_tables:
                logger.info(f"Lattice flavor found {len(good_lattice_tables)} good tables")
                for table in good_lattice_tables:
                    canonical = self._canonicalize_camelot_table(table, "camelot_lattice")
                    if canonical:
                        tables.append(canonical)
            else:
                # Fallback to stream flavor
                logger.debug("Lattice failed, trying stream flavor")
                stream_tables = camelot.read_pdf(pdf_path, flavor="stream", pages=pages)
                
                for table in stream_tables:
                    canonical = self._canonicalize_camelot_table(table, "camelot_stream") 
                    if canonical:
                        tables.append(canonical)
                        
        except Exception as e:
            logger.error(f"Camelot extraction failed: {e}")
            
        return tables
    
    async def _repair_with_pdfplumber(
        self, 
        pdf_path: str, 
        tables: List[CanonicalTable]
    ) -> List[CanonicalTable]:
        """Repair table cells using pdfplumber's text extraction."""
        if not PDFPLUMBER_AVAILABLE:
            return tables
            
        # For now, return tables as-is. This could be enhanced to:
        # 1. Use pdfplumber to extract text with precise coordinates
        # 2. Match text to table cells and repair split words
        # 3. Detect and handle rowspan/colspan scenarios
        logger.debug("pdfplumber repair placeholder - returning original tables")
        return tables
    
    async def _extract_with_gmft(
        self, 
        pdf_path: str, 
        pages: str
    ) -> List[CanonicalTable]:
        """Extract tables using GMFT (Table Transformer)."""
        if not GMFT_AVAILABLE:
            logger.warning("GMFT not available, skipping deep learning extraction")
            return []
            
        tables = []
        
        try:
            logger.debug("Running GMFT extraction")
            
            # Use GMFT programmatically
            import gmft
            
            # Initialize detector
            detector = gmft.AutoTableDetector()
            
            # Open PDF document
            doc = gmft.pdf_bindings.PyPDFium2Document(pdf_path)
            
            # Process each page
            for page_num in range(len(doc)):
                try:
                    page = doc.get_page(page_num)
                    
                    # Extract tables from the page
                    cropped_tables = detector.extract(page)
                    
                    # Convert GMFT results to canonical format
                    for i, table in enumerate(cropped_tables):
                        try:
                            canonical = self._canonicalize_gmft_table(table, page_num + 1, i)
                            if canonical:
                                tables.append(canonical)
                        except Exception as e:
                            logger.warning(f"Failed to canonicalize GMFT table {i} on page {page_num + 1}: {e}")
                            
                except Exception as e:
                    logger.warning(f"Failed to process page {page_num + 1} with GMFT: {e}")
                    
            doc.close()
            
        except Exception as e:
            logger.error(f"GMFT extraction failed: {e}")
            
        return tables
    
    def _canonicalize_camelot_table(
        self, 
        camelot_table, 
        source: str
    ) -> Optional[CanonicalTable]:
        """Convert Camelot table to canonical format."""
        try:
            df = camelot_table.df
            if df.empty:
                return None
                
            # Get bounding box
            bbox = getattr(camelot_table, '_bbox', (0, 0, 0, 0))
            
            # Convert DataFrame to list of lists
            cells = df.fillna("").astype(str).values.tolist()
            
            # Basic quality check
            if len(cells) < self.config.min_row_count:
                return None
                
            return CanonicalTable(
                id=uuid.uuid4().hex,
                source=source,
                page=camelot_table.page,
                bbox=bbox,
                cells=cells,
                confidence=camelot_table.accuracy if hasattr(camelot_table, 'accuracy') else 0.8,
                metadata={
                    "parsing_report": getattr(camelot_table, 'parsing_report', {}),
                    "shape": getattr(camelot_table, 'shape', df.shape)
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to canonicalize Camelot table: {e}")
            return None
    
    def _canonicalize_gmft_table(
        self, 
        gmft_table, 
        page_num: int,
        index: int
    ) -> Optional[CanonicalTable]:
        """Convert GMFT table to canonical format."""
        try:
            # Extract table data from GMFT CroppedTable
            
            # Get bounding box
            bbox = gmft_table.bbox if hasattr(gmft_table, 'bbox') else (0, 0, 100, 100)
            
            # Extract text content
            text_content = ""
            if hasattr(gmft_table, 'text') and callable(gmft_table.text):
                text_content = gmft_table.text()
            elif hasattr(gmft_table, 'text'):
                text_content = str(gmft_table.text)
            
            # Parse the text content into table structure
            # This is a simplified parsing - GMFT may provide structured data
            cells = self._parse_gmft_text_to_cells(text_content)
            
            if not cells or len(cells) < self.config.min_row_count:
                return None
            
            # Calculate confidence based on text quality
            confidence = self._calculate_gmft_confidence(gmft_table, cells)
            
            return CanonicalTable(
                id=uuid.uuid4().hex,
                source="gmft",
                page=page_num,
                bbox=tuple(bbox) if isinstance(bbox, (list, tuple)) else (0, 0, 100, 100),
                cells=cells,
                confidence=confidence,
                metadata={
                    "gmft_index": index,
                    "has_spans": True,  # GMFT supports rowspan/colspan
                    "text_content": text_content[:500]  # Store first 500 chars for debugging
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to canonicalize GMFT table: {e}")
            return None
    
    def _parse_gmft_text_to_cells(self, text_content: str) -> List[List[str]]:
        """Parse GMFT text content into table cells."""
        if not text_content:
            return []
        
        lines = text_content.strip().split('\n')
        cells = []
        
        for line in lines:
            if line.strip():
                # Simple parsing - split by common delimiters
                # This could be improved with more sophisticated parsing
                if '\t' in line:
                    row = [cell.strip() for cell in line.split('\t')]
                elif '|' in line:
                    row = [cell.strip() for cell in line.split('|')]
                else:
                    # Try to split by multiple spaces
                    import re
                    row = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
                
                if row:
                    cells.append(row)
        
        return cells
    
    def _calculate_gmft_confidence(self, gmft_table, cells: List[List[str]]) -> float:
        """Calculate confidence score for GMFT table."""
        base_confidence = 0.7  # Base confidence for GMFT
        
        # Adjust based on table structure
        if not cells:
            return 0.0
        
        # Check for consistent column count
        if len(cells) > 1:
            col_counts = [len(row) for row in cells]
            if len(set(col_counts)) == 1:  # All rows have same column count
                base_confidence += 0.1
        
        # Check for reasonable content
        total_chars = sum(len(cell) for row in cells for cell in row)
        if total_chars > 20:  # Reasonable amount of content
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _merge_and_deduplicate(
        self, 
        tables: List[CanonicalTable]
    ) -> List[CanonicalTable]:
        """Merge and deduplicate tables using IoU threshold."""
        if not tables:
            return []
            
        # Sort by quality score (highest first)
        sorted_tables = sorted(tables, key=lambda t: t.calculate_quality_score(), reverse=True)
        
        unique_tables = []
        
        for table in sorted_tables:
            is_duplicate = False
            
            for existing in unique_tables:
                if (table.page == existing.page and 
                    self._calculate_iou(table.bbox, existing.bbox) > self.config.iou_threshold):
                    
                    # This is a duplicate - keep the higher quality one
                    if table.calculate_quality_score() > existing.calculate_quality_score():
                        # Replace existing with this better table
                        unique_tables.remove(existing)
                        unique_tables.append(table)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_tables.append(table)
                
        return unique_tables
    
    def _calculate_iou(
        self, 
        bbox1: Tuple[float, float, float, float], 
        bbox2: Tuple[float, float, float, float]
    ) -> float:
        """Calculate Intersection over Union (IoU) for two bounding boxes."""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_int = max(x1_1, x1_2)
        y1_int = max(y1_1, y1_2)
        x2_int = min(x2_1, x2_2)
        y2_int = min(y2_1, y2_2)
        
        if x2_int <= x1_int or y2_int <= y1_int:
            return 0.0
        
        intersection = (x2_int - x1_int) * (y2_int - y1_int)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _filter_by_quality(
        self, 
        tables: List[CanonicalTable]
    ) -> List[CanonicalTable]:
        """Filter tables by quality metrics."""
        quality_tables = []
        
        for table in tables:
            # Check minimum dimensions
            if (table.row_count < self.config.min_row_count or 
                table.col_count < self.config.min_column_count):
                continue
                
            # Check empty cell ratio
            if table.empty_cell_ratio > self.config.max_empty_cell_ratio:
                continue
                
            # Check minimum confidence
            if table.confidence < self.config.min_confidence_score:
                continue
                
            # Check average cell length
            non_empty_cells = [cell for row in table.cells for cell in row if cell.strip()]
            if non_empty_cells:
                avg_length = sum(len(cell) for cell in non_empty_cells) / len(non_empty_cells)
                if avg_length < self.config.min_cell_length:
                    continue
            
            quality_tables.append(table)
            
        return quality_tables
    
    def export_to_csv(self, table: CanonicalTable, output_path: str) -> None:
        """Export table to CSV format."""
        df = pd.DataFrame(table.cells)
        df.to_csv(output_path, index=False, header=False)
        
    def export_to_markdown(self, table: CanonicalTable, output_path: str) -> None:
        """Export table to Markdown format."""
        if not table.cells:
            return
            
        lines = []
        
        # Headers
        if table.cells:
            headers = table.cells[0]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            
            # Data rows
            for row in table.cells[1:]:
                # Pad row to match header length
                padded_row = row + [""] * (len(headers) - len(row))
                lines.append("| " + " | ".join(padded_row[:len(headers)]) + " |")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


# Convenience function for integration
async def extract_tables_from_pdf(
    pdf_path: str, 
    pages: Optional[str] = "all",
    config: Optional[TableExtractionConfig] = None
) -> List[TableBlock]:
    """
    Extract tables from PDF and return as TableBlock objects.
    
    Args:
        pdf_path: Path to PDF file
        pages: Page specification
        config: Extraction configuration
        
    Returns:
        List of TableBlock objects
    """
    extractor = AdvancedTableExtractor(config)
    canonical_tables = await extractor.extract_tables(pdf_path, pages)
    
    # Convert to TableBlock objects
    table_blocks = []
    for table in canonical_tables:
        try:
            block = table.to_table_block()
            table_blocks.append(block)
        except Exception as e:
            logger.warning(f"Failed to convert table to TableBlock: {e}")
    
    return table_blocks
