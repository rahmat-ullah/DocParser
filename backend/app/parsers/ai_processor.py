"""
AI Processor for enhancing parsed content with AI-generated descriptions.
Handles images (description and table extraction) and math blocks using AI services.
"""

import asyncio
import base64
from io import BytesIO
from PIL import Image
from typing import List, Optional, AsyncGenerator

from ..services.ai_service import get_ai_service
from .ast_models import DocumentAST, ImageBlock, MathBlock, TableBlock, ParseProgress
from ..utils.image_analysis_utils import extract_table_from_pil_image
from ..core.config import settings


class AIProcessor:
    """Processor for enhancing document AST with AI-generated content."""

    async def process_ast(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """
        Process document AST and enhance with AI-generated content.
        This includes image descriptions and table extraction from images.
        """
        if progress_callback:
            await self._emit_progress(progress_callback, "ai_processing_start", 0.0, "Starting AI processing")

        # Process images for descriptions and table extraction
        await self._process_images_and_extract_tables(ast, progress_callback)
        
        # Process math blocks
        await self._process_math(ast.math, progress_callback) # Assuming this doesn't need full AST

        if progress_callback:
            await self._emit_progress(progress_callback, "ai_processing_complete", 1.0, "AI processing completed")

        return ast

    async def _process_images_and_extract_tables(
        self, 
        ast: DocumentAST, # Pass the full AST to append tables
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process image blocks: generate AI descriptions and extract tables."""
        if not ast.images:
            return

        ai_service = await get_ai_service()
        
        # Determine total steps for progress: 1 for description, 1 for table extraction (if enabled) per image
        total_image_processing_steps = len(ast.images)
        if settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED:
            total_image_processing_steps *= 2

        current_step = 0

        all_new_tables: List[TableBlock] = []

        # Define a batch size for concurrent processing
        batch_size = settings.AI_PROCESSOR_IMAGE_BATCH_SIZE or 3 # Default to 3 if not in settings

        for i in range(0, len(ast.images), batch_size):
            batch_image_blocks = ast.images[i:i + batch_size]
            
            tasks = []
            for idx_in_batch, image_block in enumerate(batch_image_blocks):
                original_idx = i + idx_in_batch
                image_name = f"image_{original_idx}_p{image_block.page if image_block.page is not None else 'unk'}"
                tasks.append(self._process_single_image_fully(
                    ai_service,
                    image_block,
                    image_name,
                    progress_callback,
                    current_step + (idx_in_batch * (2 if settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED else 1)), # initial step for this image
                    total_image_processing_steps
                ))
            
            # Run tasks for the current batch concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results from the batch
            for result in results:
                if isinstance(result, TableBlock):
                    all_new_tables.append(result)
                elif isinstance(result, Exception):
                    # Log the exception or handle as needed
                    print(f"Error during concurrent image processing: {result}")
            
            current_step += len(batch_image_blocks) * (2 if settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED else 1)
            
            # Overall batch progress (optional, could be too granular)
            if progress_callback:
                 processed_images_count = min(i + batch_size, len(ast.images))
                 await self._emit_progress(
                    progress_callback,
                    "ai_image_batch_processed",
                    current_step / total_image_processing_steps if total_image_processing_steps > 0 else 0,
                    f"Batch of {len(batch_image_blocks)} images processed ({processed_images_count}/{len(ast.images)} total images)"
                )

        if all_new_tables:
            ast.tables.extend(all_new_tables)


    async def _process_single_image_fully(
        self,
        ai_service,
        image_block: ImageBlock,
        image_name: str,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]], # For granular updates
        base_step: int, # The starting step count for this image in overall progress
        total_overall_steps: int # Total steps for all images
        ) -> Optional[TableBlock]:
        """Processes a single image for description and table extraction."""

        current_local_step = base_step

        # 1. Describe image content
        if not image_block.alt_text or image_block.alt_text.startswith("Image from"):
            try:
                await self._describe_image_content(ai_service, image_block)
            except Exception as e:
                print(f"Error describing {image_name}: {e}")
                if not image_block.alt_text:
                    image_block.alt_text = "Image (description failed)"

        current_local_step +=1
        if progress_callback:
            await self._emit_progress(
                progress_callback,
                "ai_image_description",
                current_local_step / total_overall_steps if total_overall_steps > 0 else 0,
                f"Processed description for {image_name}"
            )

        # 2. Extract table if enabled
        extracted_table: Optional[TableBlock] = None
        if settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED:
            try:
                image_bytes = base64.b64decode(image_block.data)
                pil_image = Image.open(BytesIO(image_bytes))

                extracted_table = await extract_table_from_pil_image(pil_image, image_name)
                pil_image.close()

                if extracted_table:
                    if image_block.bbox and "page" in image_block.bbox:
                        page_num = image_block.bbox["page"]
                        if extracted_table.bbox: # Should exist if table has content
                            extracted_table.bbox["page"] = page_num
                        else: # Fallback, though parse_markdown_table should init bbox if headers/rows exist
                            extracted_table.bbox = {"page": page_num}
                        # Assign other context if needed, e.g. original image bbox
                        # extracted_table.metadata = {"source_image_bbox": image_block.bbox}

            except Exception as e:
                print(f"Error extracting table from {image_name}: {e}")
            
            current_local_step +=1
            if progress_callback:
                 await self._emit_progress(
                    progress_callback,
                    "ai_image_table_extraction",
                    current_local_step / total_overall_steps if total_overall_steps > 0 else 0,
                    f"Processed table extraction for {image_name}"
                )

        return extracted_table


    async def _describe_image_content(self, ai_service, image: ImageBlock) -> None:
        """Helper to generate AI description for a single image block."""
        # (This is essentially the old _describe_image method, slightly refactored)
        context = {
            "filename": image.source if hasattr(image, 'source') and image.source else "embedded_image",
            "page": image.page if image.page is not None else 0, # Ensure page is not None
            "section": image.section if hasattr(image, 'section') and image.section else "",
            "index": image.index if image.index is not None else 0 # Ensure index is not None
        }

        metadata = await ai_service.analyze_image_structured(image.data, context)

        if hasattr(image, 'metadata'): # Should always be true for ImageBlock
            image.metadata = metadata

        image.alt_text = metadata.get('description', '') or \
                         metadata.get('aiAnnotations', {}).get('explanationGenerated', '')

        if not image.alt_text:
            ocr_text = metadata.get('aiAnnotations', {}).get('ocrText', '')
            if ocr_text:
                image.alt_text = f"Text in image: {ocr_text[:200]}{'...' if len(ocr_text) > 200 else ''}" # Limit length
            else:
                image.alt_text = "Image (no description available)"


    async def _process_math(
        self, 
        math_blocks: List[MathBlock], 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process math blocks (placeholder for future enhancements)."""
        if not math_blocks:
            return
        
        for i, math_block in enumerate(math_blocks):
            if math_block.format == "text":
                math_block.format = "latex" # Simple conversion attempt
            
            if progress_callback:
                progress = (i + 1) / len(math_blocks) if len(math_blocks) > 0 else 0
                await self._emit_progress(
                    progress_callback,
                    "ai_math_processing",
                    progress,
                    f"Processed math block {i + 1}/{len(math_blocks)}"
                )

    async def _emit_progress(
        self,
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]],
        stage: str,
        progress_val: float,
        message: str,
        details: Optional[dict] = None
    ) -> None:
        """Helper to emit progress if callback is available."""
        if progress_callback:
            progress_update = ParseProgress(
                stage=stage,
                progress=progress_val,
                message=message,
                details=details
            )
            try:
                await progress_callback.asend(progress_update)
            except (StopAsyncIteration, GeneratorExit):
                pass # Callback closed
