"""
IMG Parser for image files.
Extracts images, uses AI service to generate descriptions, and extracts tables.
"""

import base64
import pytesseract
from typing import Optional, AsyncGenerator
from pathlib import Path
from PIL import Image
import openai
import os

from .base_parser import BaseParser, ParseError
from .ast_models import DocumentAST, ImageBlock, TableBlock, ParseProgress
from ..utils.markdown_utils import parse_markdown_table_to_table_block
from ..utils.image_analysis_utils import extract_table_from_pil_image # Import new utility
from backend.app.core.config import settings # For API key

# Ensure OPENAI_API_KEY is loaded for the module
# This might be better handled if settings are passed down or globally accessible
# For now, direct import and usage from settings.
# openai.api_key = settings.OPENAI_API_KEY


class IMGParser(BaseParser):
    """Parser for image documents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # OpenAI API key is typically initialized globally when the openai library is imported
        # and settings are loaded. Explicitly setting openai.api_key here might be
        # redundant or could interfere if the client is already configured.
        # The utility function extract_table_from_pil_image now also checks settings.OPENAI_API_KEY.
        if not settings.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY is not set in settings. Table extraction from images will likely fail.")


    def supports_file(self, file_path: Path) -> bool:
        """Check if file is an image."""
        return file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    async def parse(
        self, file_path: Path, progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """Parse image document, extract content, and attempt to extract tables."""
        image_pil = None # Ensure image_pil is defined for finally block
        ast = DocumentAST() # Initialize AST early for broader scope in case of errors

        try:
            self.progress_callback = progress_callback # Store for internal methods
            await self._emit_progress(self.progress_callback, "initialization", 0.0, f"Opening image document: {file_path.name}")

            image_pil = Image.open(file_path)

            # Read and encode image for ImageBlock data
            # Re-opening file here for bytes is not ideal if PIL can give bytes, but often robust.
            # Alternatively, convert PIL image back to bytes:
            #   img_byte_arr = io.BytesIO()
            #   image_pil.save(img_byte_arr, format=image_pil.format or 'PNG') # Ensure format
            #   image_data_bytes = img_byte_arr.getvalue()
            # For simplicity, re-reading, but consider efficiency for very large files.
            with open(file_path, 'rb') as image_file_rb:
                image_data_bytes = image_file_rb.read()
            image_base64 = base64.b64encode(image_data_bytes).decode()

            image_format = image_pil.format or file_path.suffix.lstrip('.').upper() # Prefer PIL's detected format
            width, height = image_pil.size

            ast.metadata={ # Update pre-initialized AST
                "format": "IMAGE",
                "source_filename": file_path.name,
                "image_format": image_format,
                "width": width,
                "height": height
            }

            await self._emit_progress(self.progress_callback, "image_processing", 0.2, "Processing image content")

            image_block = ImageBlock(
                data=image_base64,
                format=image_format,
                alt_text=f"Image from {file_path.name}"
            )
            ast.images.append(image_block)

            await self._emit_progress(self.progress_callback, "table_extraction_start", 0.5, "Attempting table extraction from image")

            # Use the centralized utility function
            if settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED: # Check if feature is enabled
                extracted_table_block = await extract_table_from_pil_image(image_pil, file_path.name)
                if extracted_table_block:
                    ast.tables.append(extracted_table_block)
                    await self._emit_progress(self.progress_callback, "table_extraction_done", 0.8, "Table successfully extracted")
                else:
                    await self._emit_progress(self.progress_callback, "table_extraction_done", 0.8, "No table found or error during extraction")
            else:
                await self._emit_progress(self.progress_callback, "table_extraction_skipped", 0.8, "Table extraction from images is disabled by configuration.")


            await self._emit_progress(self.progress_callback, "completion", 1.0, "Image parsing and table extraction attempt completed")
            return ast

        except FileNotFoundError:
            raise ParseError(f"Image file not found: {file_path}", file_path)
        except pytesseract.TesseractError as e: # Catch specific Tesseract errors if utility func doesn't
            await self._emit_progress(self.progress_callback, "ocr_error", 0.0, f"Tesseract processing error: {e}. Check Tesseract installation and language data.")
            # Return AST without table if OCR fails but basic image parsing was okay
            # The AST is already initialized and might have basic image info
            await self._emit_progress(self.progress_callback, "completion_partial", 1.0, "Image parsed, but table extraction failed due to OCR error.")
            return ast # Return partially processed AST
        except Exception as e:
            # General exception
            await self._emit_progress(self.progress_callback, "error", 0.0, f"Failed to parse image: {str(e)}")
            # Return partially processed AST if available
            if ast.metadata or ast.images: # If some info was gathered
                 await self._emit_progress(self.progress_callback, "completion_error", 1.0, f"Image parsing completed with errors: {e}")
                 return ast
            raise ParseError(f"Failed to parse image: {str(e)}", file_path, e)
        finally:
            if image_pil: # Check if image_pil was successfully assigned
                image_pil.close()
            self.progress_callback = None # Clear callback

    async def _emit_progress(
        self,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]],
        stage: str,
        progress_val: float,
        message: str,
        details: Optional[dict] = None
    ) -> None:
        """Helper to emit progress if callback is available."""
        cb_to_use = progress_callback if progress_callback is not None else getattr(self, 'progress_callback', None)
        if cb_to_use:
            progress_update = ParseProgress(
                stage=stage,
                progress=progress_val,
                message=message,
                details=details
            )
            try:
                await cb_to_use.asend(progress_update)
            except (StopAsyncIteration, GeneratorExit):
                pass # Callback closed
