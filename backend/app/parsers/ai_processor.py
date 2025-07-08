"""
AI Processor for enhancing parsed content with AI-generated descriptions.
Handles images and math blocks using AI services.
"""

import asyncio
from typing import List, Optional, AsyncGenerator

from ..services.ai_service import get_ai_service
from .ast_models import DocumentAST, ImageBlock, MathBlock, ParseProgress


class AIProcessor:
    """Processor for enhancing document AST with AI-generated content."""

    async def process_ast(
        self, 
        ast: DocumentAST, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """
        Process document AST and enhance with AI-generated content.
        
        Args:
            ast: Document AST to process
            progress_callback: Optional progress callback
            
        Returns:
            Enhanced DocumentAST with AI-generated descriptions
        """
        if progress_callback:
            await progress_callback.asend(ParseProgress(
                stage="ai_processing",
                progress=0.0,
                message="Starting AI processing"
            ))

        # Process images
        await self._process_images(ast.images, progress_callback)
        
        # Process math blocks
        await self._process_math(ast.math, progress_callback)

        if progress_callback:
            await progress_callback.asend(ParseProgress(
                stage="ai_processing",
                progress=1.0,
                message="AI processing completed"
            ))

        return ast

    async def _process_images(
        self, 
        images: List[ImageBlock], 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process image blocks with AI descriptions."""
        if not images:
            return

        ai_service = await get_ai_service()
        
        # Process images in batches to avoid overwhelming the API
        batch_size = 5
        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for image in batch:
                if not image.alt_text or image.alt_text.startswith("Image from"):
                    # Only process if no meaningful alt text exists
                    tasks.append(self._describe_image(ai_service, image))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update progress
            if progress_callback:
                progress = min((i + batch_size) / len(images), 1.0)
                await progress_callback.asend(ParseProgress(
                    stage="ai_image_processing",
                    progress=progress,
                    message=f"Processing images: {min(i + batch_size, len(images))}/{len(images)}"
                ))

    async def _describe_image(self, ai_service, image: ImageBlock) -> None:
        """Generate AI description for a single image."""
        try:
            description = await ai_service.describe_image(image.data)
            image.alt_text = description
        except Exception as e:
            # Keep original alt text if AI fails
            if not image.alt_text:
                image.alt_text = f"Image (AI description failed: {str(e)})"

    async def _process_math(
        self, 
        math_blocks: List[MathBlock], 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> None:
        """Process math blocks (placeholder for future enhancements)."""
        if not math_blocks:
            return

        # For now, just update progress
        # Future enhancements could include:
        # - Converting between LaTeX and MathML
        # - Simplifying complex expressions
        # - Adding natural language descriptions
        
        for i, math_block in enumerate(math_blocks):
            # Placeholder processing
            if math_block.format == "text":
                # Try to convert simple text equations to LaTeX
                math_block.format = "latex"
            
            if progress_callback:
                progress = (i + 1) / len(math_blocks)
                await progress_callback.asend(ParseProgress(
                    stage="ai_math_processing",
                    progress=progress,
                    message=f"Processing math blocks: {i + 1}/{len(math_blocks)}"
                ))
