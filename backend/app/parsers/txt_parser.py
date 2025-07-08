"""
TXT Parser for plain text files.
Extracts text content and attempts to identify structure.
"""

import re
from typing import Optional, AsyncGenerator
from pathlib import Path

from .base_parser import BaseParser, ParseError
from .ast_models import DocumentAST, TextBlock, BlockType, ParseProgress


class TXTParser(BaseParser):
    """Parser for plain text documents."""

    def supports_file(self, file_path: Path) -> bool:
        """Check if file is a TXT."""
        return file_path.suffix.lower() in ['.txt', '.md', '.markdown']

    async def parse(
        self, file_path: Path, progress_callback: Optional[AsyncGenerator[ParseProgress, None]] = None
    ) -> DocumentAST:
        """Parse TXT document and extract content."""
        try:
            await self._emit_progress(progress_callback, "initialization", 0.0, "Opening text document")

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            ast = DocumentAST(metadata={"format": "TXT"})
            
            # Split into lines and process
            lines = content.split('\n')
            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                if i % 100 == 0:  # Update progress every 100 lines
                    await self._emit_progress(
                        progress_callback, 
                        "parsing_lines", 
                        i / total_lines, 
                        f"Processing line {i + 1} of {total_lines}"
                    )
                
                line = line.strip()
                if not line:
                    continue
                
                # Determine block type
                block_type, level = self._determine_block_type(line)
                
                text_block = TextBlock(
                    type=block_type,
                    content=line,
                    level=level
                )
                ast.textBlocks.append(text_block)

            await self._emit_progress(progress_callback, "completion", 1.0, "Text parsing completed")
            return ast

        except Exception as e:
            raise ParseError(f"Failed to parse TXT: {str(e)}", file_path, e)

    def _determine_block_type(self, line: str) -> tuple[BlockType, Optional[int]]:
        """Determine block type and level from text content."""
        # Check for markdown-style headings
        if line.startswith('#'):
            level = min(len(line) - len(line.lstrip('#')), 6)
            return BlockType.HEADING, level
        
        # Check for list items
        if re.match(r'^[\s]*[\-\*\+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
            return BlockType.LIST_ITEM, None
        
        # Check for code blocks (indented lines)
        if line.startswith('    ') or line.startswith('\t'):
            return BlockType.CODE, None
        
        # Check for quotes
        if line.startswith('>'):
            return BlockType.QUOTE, None
        
        # Default to paragraph
        return BlockType.PARAGRAPH, None
