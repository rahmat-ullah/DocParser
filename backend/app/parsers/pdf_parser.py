"""
PDF Parser implementation using PyMuPDF.
Extracts text, images, tables, and mathematical content from PDF files.
"""

import base64
import re
from typing import AsyncGenerator, Optional, List
from pathlib import Path
import fitz  # PyMuPDF
from io import BytesIO

from .base_parser import BaseParser, ParseError
from .ast_models import DocumentAST, TextBlock, ImageBlock, TableBlock, MathBlock, BlockType, ParseProgress


class PDFParser(BaseParser):
    """Parser for PDF documents using PyMuPDF."""

    def supports_file(self, file_path: Path) -> bool:
        """Check if file is a PDF."""
        return file_path.suffix.lower() == '.pdf'

    async def parse(
        self, 
        file_path: Path, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """Parse PDF document and extract content."""
        try:
            await self._emit_progress(progress_callback, "initialization", 0.0, "Opening PDF document")
            
            doc = fitz.open(str(file_path))
            total_pages = doc.page_count
            
            ast = DocumentAST(
                metadata={
                    "title": doc.metadata.get("title", ""),
                    "author": doc.metadata.get("author", ""),
                    "subject": doc.metadata.get("subject", ""),
                    "creator": doc.metadata.get("creator", ""),
                    "pages": total_pages,
                    "format": "PDF"
                }
            )

            for page_num in range(total_pages):
                await self._emit_progress(
                    progress_callback, 
                    "parsing_pages", 
                    page_num / total_pages, 
                    f"Processing page {page_num + 1} of {total_pages}"
                )
                
                page = doc[page_num]
                
                # Extract text blocks
                await self._extract_text_blocks(page, ast, page_num)
                
                # Extract images
                await self._extract_images(page, ast, page_num)
                
                # Extract tables using advanced table extraction service
                await self._extract_tables_enhanced(page, ast, page_num, file_path)
                
                # Extract math expressions
                await self._extract_math(page, ast, page_num)

            doc.close()
            
            await self._emit_progress(progress_callback, "completion", 1.0, "PDF parsing completed")
            return ast
            
        except Exception as e:
            raise ParseError(f"Failed to parse PDF: {str(e)}", file_path, e)

    async def _extract_text_blocks(self, page, ast: DocumentAST, page_num: int) -> None:
        """Extract text blocks from a PDF page."""
        blocks = page.get_text("dict")
        
        for block in blocks.get("blocks", []):
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                line_text = ""
                font_info = {}
                
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                    if not font_info:  # Use first span's font info
                        font_info = {
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0)
                        }
                
                if line_text.strip():
                    # Determine block type based on formatting
                    block_type = self._determine_block_type(line_text, font_info)
                    level = self._get_heading_level(font_info) if block_type == BlockType.HEADING else None
                    
                    text_block = TextBlock(
                        type=block_type,
                        content=line_text.strip(),
                        level=level,
                        style=font_info,
                        bbox={
                            "x0": line["bbox"][0],
                            "y0": line["bbox"][1],
                            "x1": line["bbox"][2],
                            "y1": line["bbox"][3],
                            "page": page_num
                        }
                    )
                    ast.textBlocks.append(text_block)

    async def _extract_images(self, page, ast: DocumentAST, page_num: int) -> None:
        """Extract images from a PDF page."""
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Convert to base64
                image_base64 = base64.b64encode(image_bytes).decode()
                
                # Get image rectangle
                img_rects = page.get_image_rects(xref)
                bbox = None
                if img_rects:
                    rect = img_rects[0]
                    bbox = {
                        "x0": rect.x0,
                        "y0": rect.y0,
                        "x1": rect.x1,
                        "y1": rect.y1,
                        "page": page_num
                    }
                
                image_block = ImageBlock(
                    data=image_base64,
                    format=image_ext.upper(),
                    bbox=bbox
                )
                ast.images.append(image_block)
                
            except Exception as e:
                # Skip problematic images
                continue

    async def _extract_tables(self, page, ast: DocumentAST, page_num: int) -> None:
        """Extract tables from a PDF page (basic implementation)."""
        # This is a simplified table detection based on text positioning
        # For better table extraction, consider using libraries like camelot-py or tabula-py
        
        blocks = page.get_text("dict")
        potential_table_blocks = []
        
        for block in blocks.get("blocks", []):
            if "lines" not in block:
                continue
            
            # Look for blocks with multiple aligned text spans
            lines_data = []
            for line in block["lines"]:
                spans_data = []
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        spans_data.append({
                            "text": text,
                            "bbox": span.get("bbox", [0, 0, 0, 0])
                        })
                if len(spans_data) > 1:  # Multiple columns might indicate a table
                    lines_data.append(spans_data)
            
            if len(lines_data) >= 2:  # At least 2 rows
                potential_table_blocks.append({
                    "lines": lines_data,
                    "bbox": block.get("bbox", [0, 0, 0, 0])
                })
        
        # Convert potential table blocks to TableBlock objects
        for table_data in potential_table_blocks:
            if len(table_data["lines"]) >= 2:
                # Use first row as headers
                headers = [span["text"] for span in table_data["lines"][0]]
                
                # Use remaining rows as data
                rows = []
                for line in table_data["lines"][1:]:
                    row = [span["text"] for span in line]
                    # Pad row to match header length
                    while len(row) < len(headers):
                        row.append("")
                    rows.append(row[:len(headers)])  # Truncate if too long
                
                table_block = TableBlock(
                    headers=headers,
                    rows=rows,
                    bbox={
                        "x0": table_data["bbox"][0],
                        "y0": table_data["bbox"][1],
                        "x1": table_data["bbox"][2],
                        "y1": table_data["bbox"][3],
                        "page": page_num
                    }
                )
                ast.tables.append(table_block)

    async def _extract_tables_enhanced(self, page, ast: DocumentAST, page_num: int, file_path: Path) -> None:
        """Extract tables using the enhanced table extraction service."""
        try:
            # Import locally to avoid circular imports
            from app.services.table_extraction_service import get_table_extraction_service
            
            # Get table extraction service
            table_service = await get_table_extraction_service()
            
            # Extract tables using the service for the entire PDF
            extracted_tables = await table_service.extract_tables_from_pdf(
                file_path, 
                extraction_method="auto"
            )
            
            # Filter tables for the current page
            page_tables = [table for table in extracted_tables 
                          if table.bbox and table.bbox.get("page") == page_num]
            
            # Add to AST
            for table in page_tables:
                ast.tables.append(table)
                
        except Exception as e:
            # Fall back to basic table extraction
            logger.warning(f"Enhanced table extraction failed for page {page_num}: {e}")
            await self._extract_tables(page, ast, page_num)

    async def _extract_math(self, page, ast: DocumentAST, page_num: int) -> None:
        """Extract mathematical expressions from a PDF page."""
        text = page.get_text()
        
        # Simple regex patterns for common math expressions
        math_patterns = [
            r'\$[^$]+\$',  # LaTeX inline math
            r'\$\$[^$]+\$\$',  # LaTeX display math
            r'\\begin\{[^}]+\}.*?\\end\{[^}]+\}',  # LaTeX environments
            r'[a-zA-Z]\s*[=]\s*[0-9a-zA-Z+\-*/^()\s]+',  # Simple equations
        ]
        
        for pattern in math_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                math_content = match.group().strip()
                
                # Determine if inline or display math
                is_inline = not (math_content.startswith('$$') or 'begin{' in math_content)
                
                math_block = MathBlock(
                    content=math_content,
                    format="latex",
                    is_inline=is_inline
                )
                ast.math.append(math_block)

    def _determine_block_type(self, text: str, font_info: dict) -> BlockType:
        """Determine the type of text block based on content and formatting."""
        # Check for list items
        if re.match(r'^\s*[•\-\*]\s+', text) or re.match(r'^\s*\d+\.\s+', text):
            return BlockType.LIST_ITEM
        
        # Check for code (monospace font or code-like patterns)
        font_name = font_info.get("font", "").lower()
        if "mono" in font_name or "courier" in font_name or "code" in font_name:
            return BlockType.CODE
        
        # Check for headings (larger font size, bold)
        font_size = font_info.get("size", 0)
        flags = font_info.get("flags", 0)
        is_bold = bool(flags & 2**4)  # Bold flag
        
        if font_size > 14 or is_bold:
            return BlockType.HEADING
        
        # Default to paragraph
        return BlockType.PARAGRAPH

    def _get_heading_level(self, font_info: dict) -> int:
        """Determine heading level based on font size."""
        font_size = font_info.get("size", 12)
        
        if font_size >= 24:
            return 1
        elif font_size >= 20:
            return 2
        elif font_size >= 18:
            return 3
        elif font_size >= 16:
            return 4
        elif font_size >= 14:
            return 5
        else:
            return 6
