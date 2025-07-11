"""
Document Processor Service - Main orchestrator for document parsing pipeline.
Coordinates parsing, AI processing, and Markdown generation.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict, Any

from ..parsers.parser_factory import ParserFactory
from ..parsers.ai_processor import AIProcessor
from ..parsers.markdown_generator import MarkdownGenerator
from ..parsers.ast_models import DocumentAST, ParseProgress
from .progress_emitter import emit_document_progress
from ..core.config import settings


class DocumentProcessor:
    """
    Main document processing service that orchestrates the parsing pipeline.
    """

    def __init__(self):
        """Initialize the document processor."""
        self.parser_factory = ParserFactory()
        self.ai_processor = AIProcessor()
        self.markdown_generator = MarkdownGenerator()

    async def process_document(
        self, 
        file_path: Path, 
        document_id: str,
        enable_ai_processing: bool = True
    ) -> AsyncGenerator[ParseProgress, None]:
        """
        Process a document through the complete pipeline.
        
        Args:
            file_path: Path to the document to process
            document_id: Unique identifier for real-time progress updates
            enable_ai_processing: Whether to use AI for image/math processing
            
        Yields:
            ParseProgress objects indicating processing status.
            The final progress object will contain the result in its `result` attribute.
        """
        try:
            # Stage 1: Initialize and validate
            progress = ParseProgress(
                stage="initialization",
                progress=0.0,
                message=f"Starting processing of {file_path.name}",
                details={"file_path": str(file_path)}
            )
            await emit_document_progress(document_id, progress)
            yield progress

            # Get appropriate parser
            parser = self.parser_factory.get_parser(file_path)
            
            # Stage 2: Parse document
            progress = ParseProgress(
                stage="parsing",
                progress=0.1,
                message="Parsing document structure",
                details={"parser": parser.__class__.__name__}
            )
            await emit_document_progress(document_id, progress)
            yield progress

            # Parse the document
            ast = await parser.parse(file_path)
            
            progress = ParseProgress(
                stage="parsing",
                progress=0.4,
                message="Document parsing completed",
                details={
                    "text_blocks": len(ast.textBlocks),
                    "images": len(ast.images),
                    "tables": len(ast.tables),
                    "math_blocks": len(ast.math)
                }
            )
            await emit_document_progress(document_id, progress)
            yield progress

            # Stage 3: AI Processing (if enabled)
            if enable_ai_processing and (ast.images or ast.math):
                progress = ParseProgress(
                    stage="ai_processing",
                    progress=0.5,
                    message="Starting AI enhancement",
                    details={"ai_enabled": True}
                )
                await emit_document_progress(document_id, progress)
                yield progress

                ast = await self.ai_processor.process_ast(ast)
                
                progress = ParseProgress(
                    stage="ai_processing",
                    progress=0.8,
                    message="AI enhancement completed"
                )
                await emit_document_progress(document_id, progress)
                yield progress
            else:
                progress = ParseProgress(
                    stage="ai_processing",
                    progress=0.8,
                    message="AI processing skipped",
                    details={"ai_enabled": False}
                )
                await emit_document_progress(document_id, progress)
                yield progress

            # Stage 4: Generate Markdown
            progress = ParseProgress(
                stage="markdown_generation",
                progress=0.9,
                message="Generating Markdown output"
            )
            await emit_document_progress(document_id, progress)
            yield progress

            markdown_content = self.markdown_generator.generate(ast)
            
            # Save markdown file
            output_dir = Path(settings.markdown_dir) / document_id
            output_dir.mkdir(parents=True, exist_ok=True)
            md_path = output_dir / f"{file_path.stem}.md"
            md_path.write_text(markdown_content, encoding="utf-8")
            
            # Stage 5: Complete
            completion_progress = ParseProgress(
                stage="completion",
                progress=1.0,
                message="Document processing completed",
                details={
                    "output_length": len(markdown_content),
                    "total_elements": len(ast.textBlocks) + len(ast.images) + len(ast.tables) + len(ast.math),
                    "markdown_path": str(md_path)
                }
            )
            # Add the result to the progress object
            completion_progress.result = markdown_content
            await emit_document_progress(document_id, completion_progress)
            yield completion_progress

        except Exception as e:
            progress = ParseProgress(
                stage="error",
                progress=0.0,
                message=f"Processing failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )
            await emit_document_progress(document_id, progress)
            yield progress
            raise


    def get_supported_formats(self) -> Dict[str, Any]:
        """
        Get information about supported file formats.
        
        Returns:
            Dictionary containing supported extensions and capabilities
        """
        return {
            "supported_extensions": self.parser_factory.get_supported_extensions(),
            "capabilities": {
                "text_extraction": True,
                "image_extraction": True,
                "table_extraction": True,
                "math_extraction": True,
                "ai_enhancement": True,
                "markdown_output": True
            }
        }
