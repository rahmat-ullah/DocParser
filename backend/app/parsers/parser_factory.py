"""
Parser factory for creating appropriate parsers based on file type.
"""

from typing import Optional, List
from pathlib import Path

from .base_parser import BaseParser, ParseError
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .xlsx_parser import XLSXParser
from .pptx_parser import PPTXParser
from .txt_parser import TXTParser
from .img_parser import IMGParser


class ParserFactory:
    """Factory for creating document parsers."""

    def __init__(self):
        """Initialize factory with all available parsers."""
        self._parsers = [
            PDFParser(),
            DOCXParser(),
            XLSXParser(),
            PPTXParser(),
            TXTParser(),
            IMGParser(),
        ]

    def get_parser(self, file_path: Path) -> BaseParser:
        """
        Get appropriate parser for the given file.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Parser instance that can handle the file
            
        Raises:
            ParseError: If no parser supports the file type
        """
        for parser in self._parsers:
            if parser.supports_file(file_path):
                return parser
        
        raise ParseError(f"No parser available for file type: {file_path.suffix}")

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of all supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        extensions = set()
        
        # Test each parser with dummy files to get supported extensions
        test_extensions = [
            '.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md', '.markdown',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'
        ]
        
        for ext in test_extensions:
            test_path = Path(f"test{ext}")
            for parser in self._parsers:
                if parser.supports_file(test_path):
                    extensions.add(ext)
                    break
        
        return sorted(extensions)
