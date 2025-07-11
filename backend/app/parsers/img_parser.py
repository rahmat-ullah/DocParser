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
from backend.app.utils.markdown_utils import parse_markdown_table_to_table_block
from backend.app.core.config import settings # For API key

# Ensure OPENAI_API_KEY is loaded for the module
# This might be better handled if settings are passed down or globally accessible
# For now, direct import and usage from settings.
# openai.api_key = settings.OPENAI_API_KEY


class IMGParser(BaseParser):
    """Parser for image documents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure API key is set when an instance is created
        # This is a fallback if not set globally before.
        if not openai.api_key and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        elif not settings.OPENAI_API_KEY:
            # This case should ideally be handled by application startup checks
            print("Warning: OPENAI_API_KEY is not set in settings.")


    def supports_file(self, file_path: Path) -> bool:
        """Check if file is an image."""
        return file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    async def _extract_table_from_image_data(self, image_pil: Image.Image, image_name: str) -> Optional[TableBlock]:
        """
        Internal method to extract table from PIL Image object using OCR and LLM.
        """
        if not openai.api_key:
            await self._emit_progress(None, "table_extraction_warning", 0.0, "OpenAI API key not configured. Skipping table extraction.")
            return None
        try:
            raw_text = pytesseract.image_to_string(image_pil)

            if not raw_text.strip():
                # No text detected, so no table
                return None

            prompt = f"""The following text was extracted from an image named '{image_name}'.
Please identify if there is a table in this text.
If a table is found, format it as a Markdown table.
If no table is found, respond with "No table found".

Raw text:
---
{raw_text}
---
Markdown table:
"""
            # Ensure openai.api_key is set before this call
            if not openai.api_key:
                 print("Error: OpenAI API key is not set prior to API call in IMGParser.")
                 # Consider how to signal this error - perhaps a specific progress update or log
                 return None


            response = await openai.chat.completions.create( # Use await for async context if client supports it, else run_in_executor
                model=settings.OPENAI_MODEL or "gpt-3.5-turbo", # Use model from settings or default
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts tables from text and formats them in Markdown."},
                    {"role": "user", "content": prompt}
                ]
            )

            markdown_table_str = response.choices[0].message.content.strip()

            if markdown_table_str.lower() == "no table found" or not markdown_table_str:
                return None

            # Parse the markdown table string into a TableBlock
            # The caption could be generic or derived from image_name
            table_block = parse_markdown_table_to_table_block(markdown_table_str, caption=f"Table from {image_name}")
            return table_block

        except pytesseract.TesseractNotFoundError:
            # Log this or send a progress update
            await self._emit_progress(None, "ocr_error", 0.0, "Tesseract is not installed or not in PATH. Skipping table extraction.")
            return None
        except openai.APIError as e:
            # Log this or send a progress update
            await self._emit_progress(None, "llm_error", 0.0, f"OpenAI API Error during table extraction: {e}. Skipping.")
            return None
        except Exception as e:
            # Log this or send a progress update
            await self._emit_progress(None, "table_extraction_error", 0.0, f"Error extracting table from image {image_name}: {e}")
            return None


    async def parse(
        self, file_path: Path, progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """Parse image document, extract content, and attempt to extract tables."""
        try:
            self.progress_callback = progress_callback # Store for internal methods
            await self._emit_progress(self.progress_callback, "initialization", 0.0, f"Opening image document: {file_path.name}")

            image_pil = Image.open(file_path)

            # Read and encode image for ImageBlock data
            with open(file_path, 'rb') as image_file_rb:
                image_data_bytes = image_file_rb.read()
                image_base64 = base64.b64encode(image_data_bytes).decode()

            image_format = file_path.suffix.lstrip('.').upper()
            width, height = image_pil.size

            ast = DocumentAST(metadata={
                "format": "IMAGE",
                "source_filename": file_path.name,
                "image_format": image_format,
                "width": width,
                "height": height
            })

            await self._emit_progress(self.progress_callback, "image_processing", 0.2, "Processing image content")

            image_block = ImageBlock(
                data=image_base64,
                format=image_format,
                alt_text=f"Image from {file_path.name}" # Placeholder, AI processor might update this
            )
            ast.images.append(image_block)

            await self._emit_progress(self.progress_callback, "table_extraction_start", 0.5, "Attempting table extraction from image")

            # Attempt to extract tables
            # Pass the PIL image object directly to avoid re-opening
            extracted_table_block = await self._extract_table_from_image_data(image_pil, file_path.name)
            if extracted_table_block:
                ast.tables.append(extracted_table_block)
                await self._emit_progress(self.progress_callback, "table_extraction_done", 0.8, "Table successfully extracted")
            else:
                await self._emit_progress(self.progress_callback, "table_extraction_done", 0.8, "No table found or error during extraction")

            await self._emit_progress(self.progress_callback, "completion", 1.0, "Image parsing and table extraction attempt completed")
            return ast

        except FileNotFoundError:
            raise ParseError(f"Image file not found: {file_path}", file_path)
        except pytesseract.TesseractError as e:
            # This handles Tesseract-specific errors not caught by TesseractNotFoundError
            await self._emit_progress(self.progress_callback, "ocr_error", 0.0, f"Tesseract processing error: {e}. Check Tesseract installation and language data.")
            # Return AST without table if OCR fails but basic image parsing was okay
            if 'ast' in locals():
                 await self._emit_progress(self.progress_callback, "completion_partial", 1.0, "Image parsed, but table extraction failed due to OCR error.")
                 return ast
            raise ParseError(f"Tesseract error during image parsing: {str(e)}", file_path, e)
        except Exception as e:
            # General exception
            if 'ast' in locals() and ast: # If AST was initialized, return it partially
                 await self._emit_progress(self.progress_callback, "completion_error", 1.0, f"Image parsing completed with errors: {e}")
                 return ast
            raise ParseError(f"Failed to parse image: {str(e)}", file_path, e)
        finally:
            if 'image_pil' in locals() and image_pil:
                image_pil.close()
            self.progress_callback = None # Clear callback

    async def _emit_progress(
        self,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]],
        stage: str,
        progress_val: float, # Renamed to avoid conflict
        message: str,
        details: Optional[dict] = None
    ) -> None:
        """Helper to emit progress if callback is available."""
        # This overrides the base class method to use self.progress_callback if progress_callback arg is None
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
