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
from ..utils.advanced_table_extractor import extract_tables_from_pdf, TableExtractionConfig


class PDFParser(BaseParser):
    """Parser for PDF documents using PyMuPDF."""

    def __init__(self):
        super().__init__()
        # Initialize advanced table extraction config
        self.table_config = TableExtractionConfig()
        # Enable both rule-based and AI-based table extraction
        self.use_advanced_table_extraction = True

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
            
            pdf_metadata = {
                "title": doc.metadata.get("title", "") or file_path.stem,
                "authors": doc.metadata.get("author", "") or "Unknown",
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "pages": total_pages,
            }
            
            base_metadata = self._create_base_metadata(file_path, pdf_metadata)
            ast = DocumentAST(metadata=base_metadata)

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
                
                # Skip basic table extraction - will be done with advanced method
                
                # Extract math expressions
                await self._extract_math(page, ast, page_num)

            doc.close()
            
            # Advanced table extraction after basic parsing
            if self.use_advanced_table_extraction:
                await self._emit_progress(
                    progress_callback, 
                    "advanced_table_extraction", 
                    0.8, 
                    "Starting advanced table extraction"
                )
                
                try:
                    # Extract tables using advanced method
                    advanced_tables = await extract_tables_from_pdf(
                        str(file_path), 
                        pages="all", 
                        config=self.table_config
                    )
                    
                    # Replace or merge with existing tables
                    if advanced_tables:
                        # Clear basic tables and use advanced ones
                        ast.tables = advanced_tables
                        
                        await self._emit_progress(
                            progress_callback, 
                            "advanced_table_extraction_complete", 
                            0.9, 
                            f"Advanced table extraction completed: {len(advanced_tables)} tables found"
                        )
                    else:
                        await self._emit_progress(
                            progress_callback, 
                            "advanced_table_extraction_complete", 
                            0.9, 
                            "Advanced table extraction completed: no tables found"
                        )
                        
                except Exception as e:
                    # Log error but don't fail parsing
                    print(f"Advanced table extraction failed: {e}")
                    await self._emit_progress(
                        progress_callback, 
                        "advanced_table_extraction_error", 
                        0.9, 
                        f"Advanced table extraction failed: {str(e)[:100]}"
                    )
            
            await self._emit_progress(progress_callback, "completion", 1.0, "PDF parsing completed")
            return ast
            
        except Exception as e:
            raise ParseError(f"Failed to parse PDF: {str(e)}", file_path, e)

    async def _extract_text_blocks(self, page, ast: DocumentAST, page_num: int) -> None:
        """Extract text blocks from a PDF page."""
        blocks = page.get_text("dict")
        block_index = 0
        
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
                        page=page_num,
                        index=block_index,
                        bbox={
                            "x0": line["bbox"][0],
                            "y0": line["bbox"][1],
                            "x1": line["bbox"][2],
                            "y1": line["bbox"][3],
                            "page": page_num,
                            "index_on_page": block_index
                        }
                    )
                    ast.textBlocks.append(text_block)
                    block_index += 1

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
                        "page": page_num,
                        "index_on_page": img_index + 1000  # Offset to sort after text
                    }
                
                image_block = ImageBlock(
                    data=image_base64,
                    format=image_ext.upper(),
                    page=page_num,
                    index=img_index + 1000,  # Offset to sort after text
                    bbox=bbox
                )
                ast.images.append(image_block)
                
            except Exception as e:
                # Skip problematic images
                continue

    async def _extract_tables_basic(self, page, ast: DocumentAST, page_num: int) -> None:
        """Extract tables from a PDF page (basic implementation - kept as fallback)."""
        # This is a simplified table detection based on text positioning
        # Now serves as a fallback if advanced extraction fails
        
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
                    },
                    metadata={
                        "extraction_method": "basic_text_alignment",
                        "extraction_source": "pdf_parser_basic",
                        "confidence": 0.6
                    }
                )
                ast.tables.append(table_block)

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
