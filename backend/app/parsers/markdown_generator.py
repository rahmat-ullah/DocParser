"""
Markdown Generator for converting DocumentAST to Markdown format.
"""

from typing import List, Optional
from .ast_models import DocumentAST, TextBlock, ImageBlock, TableBlock, MathBlock, BlockType


class MarkdownGenerator:
    """Generator for converting DocumentAST to Markdown."""

    def generate(self, ast: DocumentAST) -> str:
        """
        Generate Markdown content from DocumentAST.
        
        Args:
            ast: Document AST to convert
            
        Returns:
            Markdown string representation
        """
        markdown_parts = []
        
        # Add metadata as frontmatter (if available)
        if ast.metadata:
            frontmatter = self._generate_frontmatter(ast.metadata)
            if frontmatter:
                markdown_parts.append(frontmatter)
        
        # Process text blocks
        for text_block in ast.textBlocks:
            markdown_parts.append(self._generate_text_block(text_block))
        
        # Process images
        for image_block in ast.images:
            markdown_parts.append(self._generate_image_block(image_block))
        
        # Process tables
        for table_block in ast.tables:
            markdown_parts.append(self._generate_table_block(table_block))
        
        # Process math blocks
        for math_block in ast.math:
            markdown_parts.append(self._generate_math_block(math_block))
        
        # Join all parts with double newlines
        return '\n\n'.join(filter(None, markdown_parts))

    def _generate_frontmatter(self, metadata: dict) -> Optional[str]:
        """Generate YAML frontmatter from metadata."""
        if not metadata:
            return None
        
        # Include relevant metadata fields plus enhanced AI fields
        relevant_fields = [
            'title', 'author', 'subject', 'format', 'pages', 'sheets', 'slides',
            'document_type', 'complexity', 'contextual_summary', 'spatial_analysis'
        ]
        frontmatter_data = {k: v for k, v in metadata.items() if k in relevant_fields and v}
        
        if not frontmatter_data:
            return None
        
        lines = ['---']
        for key, value in frontmatter_data.items():
            if key == 'contextual_summary':
                # Format multiline summary properly
                lines.append(f'{key}: |')
                for line in str(value).split('\n'):
                    lines.append(f'  {line}')
            elif key == 'spatial_analysis':
                # Format spatial analysis data
                lines.append(f'{key}:')
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        lines.append(f'  {subkey}: {subvalue}')
                else:
                    lines.append(f'  {value}')
            else:
                lines.append(f'{key}: {value}')
        lines.append('---')
        
        return '\n'.join(lines)

    def _generate_text_block(self, text_block: TextBlock) -> str:
        """Generate Markdown for a text block."""
        content = text_block.content.strip()
        if not content:
            return ""
        
        if text_block.type == BlockType.HEADING:
            level = text_block.level or 1
            return f"{'#' * level} {content}"
        
        elif text_block.type == BlockType.LIST_ITEM:
            # Simple list item formatting
            if content.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                return content  # Already formatted as numbered list
            elif not content.startswith(('-', '*', '+')):
                return f"- {content}"
            else:
                return content  # Already formatted as bulleted list
        
        elif text_block.type == BlockType.CODE:
            # Code block
            return f"```\n{content}\n```"
        
        elif text_block.type == BlockType.QUOTE:
            # Quote block
            if not content.startswith('>'):
                return f"> {content}"
            else:
                return content
        
        else:  # PARAGRAPH
            return content

    def _generate_image_block(self, image_block: ImageBlock) -> str:
        """Generate Markdown for an image block with enhanced metadata."""
        alt_text = image_block.alt_text or "Image"
        caption = image_block.caption or ""
        
        # Create a markdown image reference (placeholder)
        markdown = f"![{alt_text}](data:image/{image_block.format.lower()};base64,{image_block.data[:50]}...)"
        
        # Add enhanced metadata if available
        if hasattr(image_block, 'metadata') and image_block.metadata:
            metadata = image_block.metadata
            
            # Add contextual summary if available
            contextual_summary = metadata.get('contextual_summary', '')
            if contextual_summary:
                markdown += f"\n\n**Context:** {contextual_summary}"
            
            # Add semantic tags if available
            semantic_tags = metadata.get('semantic_tags', [])
            if semantic_tags:
                markdown += f"\n\n**Tags:** {', '.join(semantic_tags)}"
            
            # Add technical details if available
            technical_details = metadata.get('technical_details', {})
            if technical_details:
                key_findings = technical_details.get('key_findings', [])
                if key_findings:
                    markdown += f"\n\n**Key Findings:**\n"
                    for finding in key_findings:
                        markdown += f"- {finding}\n"
                
                data_points = technical_details.get('data_points', [])
                if data_points:
                    markdown += f"\n**Data Points:**\n"
                    for point in data_points:
                        markdown += f"- {point}\n"
        
        # Add original caption if present
        if caption:
            markdown += f"\n\n*{caption}*"
        
        return markdown

    def _generate_table_block(self, table_block: TableBlock) -> str:
        """Generate Markdown for a table block."""
        if not table_block.headers or not table_block.rows:
            return ""
        
        lines = []
        
        # Add caption if present
        if table_block.caption:
            lines.append(f"**{table_block.caption}**\n")
        
        # Headers
        header_line = "| " + " | ".join(table_block.headers) + " |"
        lines.append(header_line)
        
        # Separator
        separator = "| " + " | ".join(["-" * len(header) for header in table_block.headers]) + " |"
        lines.append(separator)
        
        # Rows
        for row in table_block.rows:
            # Ensure row has same number of columns as headers
            padded_row = row + [""] * (len(table_block.headers) - len(row))
            padded_row = padded_row[:len(table_block.headers)]
            
            row_line = "| " + " | ".join(str(cell) for cell in padded_row) + " |"
            lines.append(row_line)
        
        return "\n".join(lines)

    def _generate_math_block(self, math_block: MathBlock) -> str:
        """Generate Markdown for a math block."""
        content = math_block.content.strip()
        
        if math_block.is_inline:
            # Inline math
            if math_block.format == "latex":
                return f"${content}$"
            else:
                return content
        else:
            # Display math
            if math_block.format == "latex":
                return f"$$\n{content}\n$$"
            else:
                return f"```math\n{content}\n```"
