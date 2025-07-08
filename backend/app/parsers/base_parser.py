"""
Base parser interface for document parsing.
All parsers should inherit from this base class.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path

from .ast_models import DocumentAST, ParseProgress


class BaseParser(ABC):
    """Base class for all document parsers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize parser with optional configuration.
        
        Args:
            config: Parser-specific configuration options
        """
        self.config = config or {}

    @abstractmethod
    async def parse(
        self, 
        file_path: Path, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """
        Parse a document and return its AST representation.
        
        Args:
            file_path: Path to the document file
            progress_callback: Optional callback for progress updates
            
        Returns:
            DocumentAST containing parsed content
            
        Raises:
            ParseError: If parsing fails
        """
        pass

    @abstractmethod
    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this parser supports the given file type.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the parser can handle this file type
        """
        pass

    async def parse_to_dict(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a document and return its content as a dictionary.
        This provides a simpler interface as requested: parse(file_path) -> dict.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing parsed content
            
        Raises:
            ParseError: If parsing fails
        """
        ast = await self.parse(file_path)
        return ast.model_dump()

    async def _emit_progress(
        self, 
        progress_callback: Optional[AsyncGenerator[ParseProgress, None]], 
        stage: str, 
        progress: float, 
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit progress update if callback is provided.
        
        Args:
            progress_callback: Progress callback generator
            stage: Current parsing stage
            progress: Progress percentage (0.0 to 1.0)
            message: Human-readable progress message
            details: Optional additional details
        """
        if progress_callback:
            progress_update = ParseProgress(
                stage=stage,
                progress=progress,
                message=message,
                details=details
            )
            try:
                await progress_callback.asend(progress_update)
            except (StopAsyncIteration, GeneratorExit):
                # Progress callback is closed
                pass


class ParseError(Exception):
    """Exception raised when document parsing fails."""
    
    def __init__(self, message: str, file_path: Optional[Path] = None, cause: Optional[Exception] = None):
        super().__init__(message)
        self.file_path = file_path
        self.cause = cause
