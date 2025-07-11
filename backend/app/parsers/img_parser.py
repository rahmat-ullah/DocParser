"""
IMG Parser for image files.
Extracts images and uses AI service to generate descriptions.
"""

import base64
from typing import Optional, AsyncGenerator
from pathlib import Path
from PIL import Image

from .base_parser import BaseParser, ParseError
from .ast_models import DocumentAST, ImageBlock, ParseProgress


class IMGParser(BaseParser):
    """Parser for image documents."""

    def supports_file(self, file_path: Path) -> bool:
        """Check if file is an image."""
        return file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    async def parse(
        self, file_path: Path, progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """Parse image document and extract content."""
        try:
            await self._emit_progress(progress_callback, "initialization", 0.0, "Opening image document")

            # Read and encode image
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode()

            # Get image format
            image_format = file_path.suffix.lstrip('.').upper()

            # Get image dimensions
            with Image.open(file_path) as img:
                width, height = img.size

            ast = DocumentAST(metadata={
                "format": "IMAGE",
                "image_format": image_format,
                "width": width,
                "height": height
            })

            await self._emit_progress(progress_callback, "processing_image", 0.5, "Processing image content")

            # Create image block
            image_block = ImageBlock(
                data=image_base64,
                format=image_format,
                alt_text=f"Image from {file_path.name}"
            )
            ast.images.append(image_block)

            # Try to extract tables from the image
            await self._emit_progress(progress_callback, "table_extraction", 0.7, "Extracting tables from image")
            try:
                # Import locally to avoid circular imports
                from app.services.table_extraction_service import get_table_extraction_service
                
                table_service = await get_table_extraction_service()
                extracted_tables = await table_service.extract_tables_from_image(
                    file_path,
                    extraction_method="auto"
                )
                
                # Add extracted tables to AST
                for table in extracted_tables:
                    ast.tables.append(table)
                    
                if extracted_tables:
                    await self._emit_progress(progress_callback, "table_extraction", 0.9, f"Found {len(extracted_tables)} tables in image")
                    
            except Exception as e:
                # Table extraction failure shouldn't fail the entire parsing
                await self._emit_progress(progress_callback, "table_extraction", 0.9, f"Table extraction failed: {str(e)}")

            await self._emit_progress(progress_callback, "completion", 1.0, "Image parsing completed")
            return ast

        except Exception as e:
            raise ParseError(f"Failed to parse image: {str(e)}", file_path, e)
