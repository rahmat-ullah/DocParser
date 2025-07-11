"""
Table extraction service for detecting and extracting tables from documents.
Supports multiple extraction methods including rule-based and AI-enhanced approaches.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import base64
import io
from PIL import Image
import cv2
import numpy as np

# pdfplumber for table extraction
import pdfplumber

# EasyOCR for OCR-based table extraction (optional)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from app.parsers.ast_models import TableBlock
from app.services.ai_service import get_ai_service
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TableExtractionService:
    """
    Service for extracting tables from various document types.
    
    Supports multiple extraction methods:
    1. Rule-based extraction using pdfplumber
    2. OCR-based extraction using EasyOCR
    3. AI-enhanced extraction using OpenAI Vision API
    """
    
    def __init__(self):
        """Initialize the table extraction service."""
        self.ocr_reader = None
        self.ai_service = None
        self._init_ocr_reader()
    
    def _init_ocr_reader(self):
        """Initialize OCR reader lazily."""
        if not EASYOCR_AVAILABLE:
            logger.warning("EasyOCR not available - OCR-based table extraction will be disabled")
            self.ocr_reader = None
            return
            
        try:
            self.ocr_reader = easyocr.Reader(['en', 'ch_sim', 'ch_tra'])
            logger.info("OCR reader initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize OCR reader: {e}")
            logger.info("OCR-based table extraction will be disabled")
            self.ocr_reader = None
    
    async def _get_ai_service(self):
        """Get AI service instance lazily."""
        if self.ai_service is None:
            self.ai_service = await get_ai_service()
        return self.ai_service
    
    async def extract_tables_from_pdf(
        self,
        pdf_path: Path,
        extraction_method: str = "auto",
        table_settings: Optional[Dict[str, Any]] = None
    ) -> List[TableBlock]:
        """
        Extract tables from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            extraction_method: Method to use ('pdfplumber', 'ocr', 'ai', 'auto')
            table_settings: Settings for table extraction
            
        Returns:
            List of TableBlock objects containing extracted tables
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        tables = []
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = await self._extract_tables_from_page(
                        page, page_num, extraction_method, table_settings
                    )
                    tables.extend(page_tables)
                    
        except Exception as e:
            logger.error(f"Error extracting tables from PDF {pdf_path}: {e}")
            raise
        
        return tables
    
    async def _extract_tables_from_page(
        self,
        page: pdfplumber.page.Page,
        page_num: int,
        extraction_method: str,
        table_settings: Optional[Dict[str, Any]] = None
    ) -> List[TableBlock]:
        """
        Extract tables from a single PDF page.
        
        Args:
            page: pdfplumber page object
            page_num: Page number
            extraction_method: Extraction method to use
            table_settings: Table extraction settings
            
        Returns:
            List of TableBlock objects
        """
        tables = []
        
        # Set default table settings
        if table_settings is None:
            table_settings = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 3,
                "join_tolerance": 3,
                "edge_min_length": 3,
                "min_words_vertical": 3,
                "min_words_horizontal": 1,
                "intersection_tolerance": 3,
                "text_tolerance": 3,
            }
        
        try:
            if extraction_method in ["pdfplumber", "auto"]:
                # Use pdfplumber for table extraction
                pdfplumber_tables = await self._extract_with_pdfplumber(
                    page, page_num, table_settings
                )
                tables.extend(pdfplumber_tables)
            
            # If auto method and no tables found, try OCR
            if extraction_method == "auto" and not tables:
                ocr_tables = await self._extract_with_ocr(page, page_num)
                tables.extend(ocr_tables)
            
            # If OCR method explicitly requested
            if extraction_method == "ocr":
                ocr_tables = await self._extract_with_ocr(page, page_num)
                tables.extend(ocr_tables)
            
            # If AI method requested
            if extraction_method == "ai":
                ai_tables = await self._extract_with_ai(page, page_num)
                tables.extend(ai_tables)
                
        except Exception as e:
            logger.error(f"Error extracting tables from page {page_num}: {e}")
        
        return tables
    
    async def _extract_with_pdfplumber(
        self,
        page: pdfplumber.page.Page,
        page_num: int,
        table_settings: Dict[str, Any]
    ) -> List[TableBlock]:
        """
        Extract tables using pdfplumber.
        
        Args:
            page: pdfplumber page object
            page_num: Page number
            table_settings: Table extraction settings
            
        Returns:
            List of TableBlock objects
        """
        tables = []
        
        try:
            # Find tables on the page
            detected_tables = page.find_tables(table_settings=table_settings)
            
            for table_idx, table in enumerate(detected_tables):
                # Extract table data
                table_data = table.extract()
                
                if not table_data or len(table_data) == 0:
                    continue
                
                # Process table data
                headers = []
                rows = []
                
                if len(table_data) > 0:
                    # Use first row as headers if it looks like headers
                    if self._is_header_row(table_data[0]):
                        headers = [cell or "" for cell in table_data[0]]
                        rows = [[cell or "" for cell in row] for row in table_data[1:]]
                    else:
                        # Create generic headers if no clear header row
                        headers = [f"Column {i+1}" for i in range(len(table_data[0]))]
                        rows = [[cell or "" for cell in row] for row in table_data]
                
                # Create TableBlock
                table_block = TableBlock(
                    headers=headers,
                    rows=rows,
                    bbox={
                        "x0": table.bbox[0],
                        "y0": table.bbox[1],
                        "x1": table.bbox[2],
                        "y1": table.bbox[3],
                        "page": page_num
                    },
                    caption=f"Table {table_idx + 1} from page {page_num + 1}",
                    style={
                        "extraction_method": "pdfplumber",
                        "table_settings": table_settings
                    }
                )
                
                tables.append(table_block)
                
        except Exception as e:
            logger.error(f"Error in pdfplumber extraction: {e}")
        
        return tables
    
    async def _extract_with_ocr(
        self,
        page: pdfplumber.page.Page,
        page_num: int
    ) -> List[TableBlock]:
        """
        Extract tables using OCR (for cases where pdfplumber fails).
        
        Args:
            page: pdfplumber page object
            page_num: Page number
            
        Returns:
            List of TableBlock objects
        """
        tables = []
        
        if not self.ocr_reader:
            logger.warning("OCR reader not available, skipping OCR extraction")
            return tables
        
        try:
            # Convert page to image
            page_image = page.to_image(resolution=300)
            image_array = np.array(page_image.original)
            
            # Detect tables using simple heuristics
            table_regions = self._detect_table_regions(image_array)
            
            for table_idx, region in enumerate(table_regions):
                # Extract table region
                x1, y1, x2, y2 = region
                table_image = image_array[y1:y2, x1:x2]
                
                # Perform OCR on table region
                ocr_result = self.ocr_reader.readtext(table_image)
                
                # Convert OCR result to table structure
                table_data = self._ocr_to_table_structure(ocr_result, table_image.shape)
                
                if table_data:
                    headers = table_data[0] if table_data else []
                    rows = table_data[1:] if len(table_data) > 1 else []
                    
                    table_block = TableBlock(
                        headers=headers,
                        rows=rows,
                        bbox={
                            "x0": x1,
                            "y0": y1,
                            "x1": x2,
                            "y1": y2,
                            "page": page_num
                        },
                        caption=f"Table {table_idx + 1} from page {page_num + 1} (OCR)",
                        style={
                            "extraction_method": "ocr",
                            "confidence": self._calculate_ocr_confidence(ocr_result)
                        }
                    )
                    
                    tables.append(table_block)
                    
        except Exception as e:
            logger.error(f"Error in OCR extraction: {e}")
        
        return tables
    
    async def _extract_with_ai(
        self,
        page: pdfplumber.page.Page,
        page_num: int
    ) -> List[TableBlock]:
        """
        Extract tables using AI (OpenAI Vision API).
        
        Args:
            page: pdfplumber page object
            page_num: Page number
            
        Returns:
            List of TableBlock objects
        """
        tables = []
        
        try:
            ai_service = await self._get_ai_service()
            
            # Convert page to image
            page_image = page.to_image(resolution=300)
            image_buffer = io.BytesIO()
            page_image.save(image_buffer, format="PNG")
            image_base64 = base64.b64encode(image_buffer.getvalue()).decode()
            
            # Prepare context for AI analysis
            context = {
                "document_type": "pdf",
                "page_number": page_num + 1,
                "task": "table_extraction"
            }
            
            # Use AI to analyze and extract tables
            ai_result = await ai_service.analyze_image_structured(image_base64, context)
            
            # Process AI result to extract table information
            if ai_result and "tables" in ai_result:
                for table_idx, table_info in enumerate(ai_result["tables"]):
                    table_block = TableBlock(
                        headers=table_info.get("headers", []),
                        rows=table_info.get("rows", []),
                        bbox=table_info.get("bbox", {}),
                        caption=table_info.get("caption", f"Table {table_idx + 1} from page {page_num + 1} (AI)"),
                        style={
                            "extraction_method": "ai",
                            "confidence": table_info.get("confidence", 0.0)
                        }
                    )
                    
                    tables.append(table_block)
                    
        except Exception as e:
            logger.error(f"Error in AI extraction: {e}")
        
        return tables
    
    def _detect_table_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect table regions in an image using computer vision.
        
        Args:
            image: Image array
            
        Returns:
            List of bounding boxes (x1, y1, x2, y2) for detected tables
        """
        regions = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Detect horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Detect vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Find contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 5000:  # Filter small regions
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append((x, y, x + w, y + h))
                    
        except Exception as e:
            logger.error(f"Error detecting table regions: {e}")
        
        return regions
    
    def _ocr_to_table_structure(
        self,
        ocr_result: List[Tuple],
        image_shape: Tuple[int, int]
    ) -> List[List[str]]:
        """
        Convert OCR results to table structure.
        
        Args:
            ocr_result: OCR result from EasyOCR
            image_shape: Shape of the image (height, width)
            
        Returns:
            List of rows, where each row is a list of cell values
        """
        if not ocr_result:
            return []
        
        # Group OCR results by rows based on y-coordinates
        rows = {}
        
        for bbox, text, confidence in ocr_result:
            if confidence < 0.5:  # Skip low confidence text
                continue
            
            # Calculate center y-coordinate
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            
            # Find or create row
            row_key = None
            for existing_y in rows.keys():
                if abs(y_center - existing_y) < 20:  # 20 pixel tolerance
                    row_key = existing_y
                    break
            
            if row_key is None:
                row_key = y_center
                rows[row_key] = []
            
            # Add text with x-coordinate for sorting
            x_center = (bbox[0][0] + bbox[2][0]) / 2
            rows[row_key].append((x_center, text))
        
        # Sort rows by y-coordinate and cells by x-coordinate
        sorted_rows = []
        for y_coord in sorted(rows.keys()):
            row_cells = sorted(rows[y_coord], key=lambda x: x[0])
            sorted_rows.append([cell[1] for cell in row_cells])
        
        return sorted_rows
    
    def _calculate_ocr_confidence(self, ocr_result: List[Tuple]) -> float:
        """
        Calculate average confidence score from OCR results.
        
        Args:
            ocr_result: OCR result from EasyOCR
            
        Returns:
            Average confidence score
        """
        if not ocr_result:
            return 0.0
        
        total_confidence = sum(confidence for _, _, confidence in ocr_result)
        return total_confidence / len(ocr_result)
    
    def _is_header_row(self, row: List[str]) -> bool:
        """
        Determine if a row is likely a header row.
        
        Args:
            row: List of cell values
            
        Returns:
            True if row appears to be a header
        """
        if not row:
            return False
        
        # Check if cells contain typical header characteristics
        header_indicators = 0
        
        for cell in row:
            if not cell:
                continue
            
            cell_lower = cell.lower()
            
            # Check for common header words
            if any(word in cell_lower for word in [
                'name', 'date', 'time', 'id', 'type', 'status', 'amount', 'total',
                'description', 'quantity', 'price', 'number', 'code', 'category'
            ]):
                header_indicators += 1
            
            # Check for capitalized text
            if cell.isupper() or cell.istitle():
                header_indicators += 1
        
        # If more than half the cells look like headers
        return header_indicators > len(row) / 2
    
    def format_table_to_markdown(self, table: TableBlock) -> str:
        """
        Format a table to markdown format.
        
        Args:
            table: TableBlock object
            
        Returns:
            Markdown formatted table string
        """
        if not table.headers and not table.rows:
            return ""
        
        markdown_lines = []
        
        # Add headers
        if table.headers:
            header_line = "| " + " | ".join(table.headers) + " |"
            markdown_lines.append(header_line)
            
            # Add separator line
            separator_line = "| " + " | ".join(["---"] * len(table.headers)) + " |"
            markdown_lines.append(separator_line)
        
        # Add rows
        for row in table.rows:
            # Pad row to match header length if needed
            padded_row = row + [""] * (len(table.headers) - len(row))
            row_line = "| " + " | ".join(padded_row) + " |"
            markdown_lines.append(row_line)
        
        return "\n".join(markdown_lines)
    
    async def extract_tables_from_image(
        self,
        image_path: Path,
        extraction_method: str = "auto"
    ) -> List[TableBlock]:
        """
        Extract tables from an image file.
        
        Args:
            image_path: Path to the image file
            extraction_method: Method to use ('ocr', 'ai', 'auto')
            
        Returns:
            List of TableBlock objects
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        tables = []
        
        try:
            # Load image
            image = Image.open(image_path)
            image_array = np.array(image)
            
            if extraction_method in ["ocr", "auto"]:
                # Use OCR for table extraction
                if self.ocr_reader:
                    ocr_result = self.ocr_reader.readtext(image_array)
                    table_data = self._ocr_to_table_structure(ocr_result, image_array.shape)
                    
                    if table_data:
                        headers = table_data[0] if table_data else []
                        rows = table_data[1:] if len(table_data) > 1 else []
                        
                        table_block = TableBlock(
                            headers=headers,
                            rows=rows,
                            bbox={
                                "x0": 0,
                                "y0": 0,
                                "x1": image_array.shape[1],
                                "y1": image_array.shape[0],
                                "page": 0
                            },
                            caption=f"Table from {image_path.name}",
                            style={
                                "extraction_method": "ocr",
                                "confidence": self._calculate_ocr_confidence(ocr_result)
                            }
                        )
                        
                        tables.append(table_block)
            
            # Try AI extraction if auto method and no results, or if explicitly requested
            if (extraction_method == "auto" and not tables) or extraction_method == "ai":
                try:
                    ai_service = await self._get_ai_service()
                    
                    # Convert image to base64
                    image_buffer = io.BytesIO()
                    image.save(image_buffer, format="PNG")
                    image_base64 = base64.b64encode(image_buffer.getvalue()).decode()
                    
                    # Prepare context
                    context = {
                        "document_type": "image",
                        "filename": image_path.name,
                        "task": "table_extraction"
                    }
                    
                    # Use AI to analyze and extract tables
                    ai_result = await ai_service.analyze_image_structured(image_base64, context)
                    
                    if ai_result and "tables" in ai_result:
                        for table_idx, table_info in enumerate(ai_result["tables"]):
                            table_block = TableBlock(
                                headers=table_info.get("headers", []),
                                rows=table_info.get("rows", []),
                                bbox=table_info.get("bbox", {}),
                                caption=table_info.get("caption", f"Table {table_idx + 1} from {image_path.name}"),
                                style={
                                    "extraction_method": "ai",
                                    "confidence": table_info.get("confidence", 0.0)
                                }
                            )
                            
                            tables.append(table_block)
                            
                except Exception as e:
                    logger.error(f"Error in AI extraction from image: {e}")
                    
        except Exception as e:
            logger.error(f"Error extracting tables from image {image_path}: {e}")
            raise
        
        return tables


# Global instance
_table_extraction_service = None


async def get_table_extraction_service() -> TableExtractionService:
    """
    Get the global table extraction service instance.
    
    Returns:
        TableExtractionService instance
    """
    global _table_extraction_service
    if _table_extraction_service is None:
        _table_extraction_service = TableExtractionService()
    return _table_extraction_service 