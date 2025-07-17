"""
Canonical Markdown Generator for converting DocumentAST to structured Markdown format.
Follows the specified canonical layout with proper ordering and visual content formatting.
"""

from typing import List, Optional, Dict, Any, Union
from .ast_models import DocumentAST, TextBlock, ImageBlock, TableBlock, MathBlock, BlockType
import re


class ChunkElement:
    """Represents a chunk element with ordering information."""
    
    def __init__(self, element: Union[TextBlock, ImageBlock, TableBlock, MathBlock], 
                 page: int, index_on_page: int, element_type: str):
        self.element = element
        self.page = page
        self.index_on_page = index_on_page
        self.element_type = element_type
        self.sort_key = (page, index_on_page)


class MarkdownGenerator:
    """Generator for converting DocumentAST to canonical Markdown format."""

    def generate(self, ast: DocumentAST) -> str:
        """
        Generate canonical Markdown content from DocumentAST.
        
        Args:
            ast: Document AST to convert
            
        Returns:
            Canonical Markdown string representation
        """
        # Extract metadata
        metadata = ast.metadata or {}
        title = metadata.get('title', 'Document')
        source_file = metadata.get('source_file', 'Unknown')
        authors = metadata.get('authors', metadata.get('author', 'Unknown'))
        created = metadata.get('created', metadata.get('created_date', 'Unknown'))
        
        # Start building markdown
        markdown_parts = []
        
        # H1 Title
        markdown_parts.append(f"# {title}")
        markdown_parts.append(f"*Source file: {source_file}*")
        markdown_parts.append(f"*Authors: {authors}*")
        markdown_parts.append(f"*Created: {created}*")
        markdown_parts.append("")
        
        # Collect all chunks and sort them by page and index
        chunks = self._collect_and_sort_chunks(ast)
        
        # Generate Table of Contents
        toc = self._generate_table_of_contents(chunks)
        if toc:
            markdown_parts.append("## Table of Contents")
            markdown_parts.append(toc)
            markdown_parts.append("")
        
        # Process chunks in order
        current_section = None
        figure_counter = 0
        table_counter = 0
        
        for chunk in chunks:
            if chunk.element_type == 'text' and chunk.element.type == BlockType.HEADING:
                # Handle section headings
                current_section = self._generate_section_heading(chunk.element)
                markdown_parts.append(current_section)
            elif chunk.element_type == 'text':
                # Handle regular text
                text_content = self._generate_text_block(chunk.element)
                if text_content.strip():
                    markdown_parts.append(text_content)
            elif chunk.element_type == 'image':
                # Handle images with canonical format
                figure_counter += 1
                image_content = self._generate_canonical_image(chunk.element, figure_counter)
                markdown_parts.append(image_content)
            elif chunk.element_type == 'table':
                # Handle tables with canonical format
                table_counter += 1
                table_content = self._generate_canonical_table(chunk.element, table_counter)
                markdown_parts.append(table_content)
            elif chunk.element_type == 'math':
                # Handle math blocks
                math_content = self._generate_math_block(chunk.element)
                if math_content.strip():
                    markdown_parts.append(math_content)
        
        # Join all parts with proper spacing
        return '\n\n'.join(filter(None, markdown_parts))
    
    def _collect_and_sort_chunks(self, ast: DocumentAST) -> List[ChunkElement]:
        """Collect all chunks and sort them by page and index_on_page."""
        chunks = []
        
        # Collect text blocks
        for text_block in ast.textBlocks:
            page = self._get_page_from_element(text_block)
            index = self._get_index_from_element(text_block)
            chunks.append(ChunkElement(text_block, page, index, 'text'))
        
        # Collect images
        for image_block in ast.images:
            page = self._get_page_from_element(image_block)
            index = self._get_index_from_element(image_block)
            chunks.append(ChunkElement(image_block, page, index, 'image'))
        
        # Collect tables
        for table_block in ast.tables:
            page = self._get_page_from_element(table_block)
            index = self._get_index_from_element(table_block)
            chunks.append(ChunkElement(table_block, page, index, 'table'))
        
        # Collect math blocks
        for math_block in ast.math:
            page = self._get_page_from_element(math_block)
            index = self._get_index_from_element(math_block)
            chunks.append(ChunkElement(math_block, page, index, 'math'))
        
        # Sort by page then index
        chunks.sort(key=lambda x: x.sort_key)
        return chunks
    
    def _get_page_from_element(self, element) -> int:
        """Extract page number from element."""
        if hasattr(element, 'page') and element.page is not None:
            return element.page
        if hasattr(element, 'bbox') and element.bbox and 'page' in element.bbox:
            return element.bbox['page']
        return 0
    
    def _get_index_from_element(self, element) -> int:
        """Extract index_on_page from element."""
        if hasattr(element, 'index') and element.index is not None:
            return element.index
        if hasattr(element, 'order') and element.order is not None:
            return element.order
        if hasattr(element, 'bbox') and element.bbox and 'index_on_page' in element.bbox:
            return element.bbox['index_on_page']
        return 0
    
    def _generate_table_of_contents(self, chunks: List[ChunkElement]) -> str:
        """Generate table of contents from headings."""
        toc_lines = []
        
        for chunk in chunks:
            if (chunk.element_type == 'text' and 
                chunk.element.type == BlockType.HEADING and 
                chunk.element.level and chunk.element.level <= 3):
                
                # Create anchor link
                anchor = self._create_anchor(chunk.element.content)
                level = chunk.element.level
                indent = "  " * (level - 1)
                
                if level == 2:
                    toc_lines.append(f"{indent}- [{chunk.element.content}](#{anchor})")
                elif level == 3:
                    toc_lines.append(f"{indent}- [{chunk.element.content}](#{anchor})")
        
        return "\n".join(toc_lines) if toc_lines else ""
    
    def _create_anchor(self, text: str) -> str:
        """Create anchor link from text."""
        # Convert to lowercase and replace spaces with hyphens
        anchor = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor.strip('-')
    
    def _generate_section_heading(self, text_block: TextBlock) -> str:
        """Generate section heading with proper level."""
        level = text_block.level or 2
        # Cap at H3 for canonical format
        if level == 1:
            level = 2
        elif level > 3:
            level = 3
        
        heading_prefix = "#" * level
        return f"{heading_prefix} {text_block.content.strip()}"
    
    def _generate_canonical_image(self, image_block: ImageBlock, figure_number: int) -> str:
        """Generate canonical image format with rich multi-part description."""
        lines = []
        
        # Determine image type
        image_type = self._determine_image_type(image_block)
        
        # Generate heading with short caption
        short_caption = self._get_short_caption(image_block)
        lines.append(f"#### Figure {figure_number} — {short_caption}")
        lines.append("")
        
        # Generate image embed with proper alt text
        alt_text = self._get_accessible_alt_text(image_block, figure_number)
        # Wrap base64 data at 120 chars for readability
        base64_data = self._wrap_base64_data(image_block.data)
        lines.append(f"![Figure {figure_number}: {alt_text}](data:image/{image_block.format.lower()};base64,{base64_data})")
        lines.append("")
        
        # Add rich multi-part description
        lines.extend(self._generate_rich_visual_description(image_block, image_type))
        
        return "\n".join(lines)
    
    def _determine_image_type(self, image_block: ImageBlock) -> str:
        """Determine if image is a diagram or regular image."""
        # Check metadata for type information
        if hasattr(image_block, 'metadata') and image_block.metadata:
            image_type = image_block.metadata.get('type', '').lower()
            if any(keyword in image_type for keyword in ['diagram', 'flowchart', 'chart', 'graph', 'flow']):
                return 'DIAGRAM'
        
        # Check alt text for diagram indicators
        alt_text = (image_block.alt_text or '').lower()
        if any(keyword in alt_text for keyword in ['diagram', 'flowchart', 'chart', 'graph', 'flow', 'process']):
            return 'DIAGRAM'
        
        return 'IMAGE'
    
    def _get_image_title(self, image_block: ImageBlock) -> str:
        """Get or generate image title."""
        if hasattr(image_block, 'metadata') and image_block.metadata:
            title = image_block.metadata.get('title', '')
            if title:
                return title
        
        if image_block.caption:
            return image_block.caption
        
        if image_block.alt_text:
            return image_block.alt_text
        
        return "Untitled Image"
    
    def _generate_diagram_context(self, image_block: ImageBlock) -> List[str]:
        """Generate diagram-specific context blocks."""
        lines = []
        
        # Diagram Summary
        summary = self._extract_diagram_summary(image_block)
        lines.append(f"> **Diagram Summary:** {summary}")
        
        # Diagram Details
        details = self._extract_diagram_details(image_block)
        if details:
            lines.append("> **Diagram Details:**")
            for detail in details:
                lines.append(f"> • {detail}")
        
        # Diagram Flow
        flow = self._extract_diagram_flow(image_block)
        if flow:
            lines.append("> **Diagram Flow:**")
            for i, step in enumerate(flow, 1):
                lines.append(f"> {i}. {step}")
        
        return lines
    
    def _generate_image_context(self, image_block: ImageBlock) -> List[str]:
        """Generate regular image context block."""
        lines = []
        
        # Image Context
        context = self._extract_image_context(image_block)
        lines.append(f"> **Image Context:** {context}")
        
        return lines
    
    def _extract_diagram_summary(self, image_block: ImageBlock) -> str:
        """Extract or generate diagram summary."""
        if hasattr(image_block, 'metadata') and image_block.metadata:
            summary = image_block.metadata.get('contextual_summary', '')
            if summary:
                return summary
            
            # Try description
            description = image_block.metadata.get('description', '')
            if description:
                return description[:100] + ('...' if len(description) > 100 else '')
        
        return "Diagram showing process flow and relationships."
    
    def _extract_diagram_details(self, image_block: ImageBlock) -> List[str]:
        """Extract diagram details/components."""
        details = []
        
        if hasattr(image_block, 'metadata') and image_block.metadata:
            # Check technical details
            tech_details = image_block.metadata.get('technical_details', {})
            if isinstance(tech_details, dict):
                key_findings = tech_details.get('key_findings', [])
                if key_findings:
                    details.extend(key_findings[:3])  # Limit to 3 key findings
            
            # Check semantic tags for components
            tags = image_block.metadata.get('semantic_tags', [])
            if tags:
                details.append(f"Components: {', '.join(tags[:5])}")  # Limit to 5 tags
        
        return details or ["Key components and relationships are shown"]
    
    def _extract_diagram_flow(self, image_block: ImageBlock) -> List[str]:
        """Extract diagram flow/steps."""
        flow_steps = []
        
        if hasattr(image_block, 'metadata') and image_block.metadata:
            # Check for flow information in AI annotations
            ai_annotations = image_block.metadata.get('aiAnnotations', {})
            explanation = ai_annotations.get('explanationGenerated', '')
            
            if explanation:
                # Try to extract steps from explanation
                steps = re.findall(r'\d+[.):]\s*([^\n]+)', explanation)
                if steps:
                    flow_steps = steps[:5]  # Limit to 5 steps
        
        return flow_steps or ["Process flow steps are illustrated in the diagram"]
    
    def _extract_image_context(self, image_block: ImageBlock) -> str:
        """Extract image context description."""
        if hasattr(image_block, 'metadata') and image_block.metadata:
            context = image_block.metadata.get('contextual_summary', '')
            if context:
                return context
            
            description = image_block.metadata.get('description', '')
            if description:
                return description
        
        return "Image provides visual context and additional information."
    
    def _get_short_caption(self, image_block: ImageBlock) -> str:
        """Get short caption for figure heading."""
        if hasattr(image_block, 'metadata') and image_block.metadata:
            title = image_block.metadata.get('title', '')
            if title:
                return self._truncate_text(title, 80)
        
        if image_block.caption:
            return self._truncate_text(image_block.caption, 80)
        
        if image_block.alt_text:
            return self._truncate_text(image_block.alt_text, 80)
        
        return "Visual Element"
    
    def _get_accessible_alt_text(self, image_block: ImageBlock, figure_number: int) -> str:
        """Get accessible alt text (≤150 words) for screen readers."""
        # Extract alt text from metadata or fallback
        alt_text = ""
        
        if hasattr(image_block, 'metadata') and image_block.metadata:
            # Try description first
            description = image_block.metadata.get('description', '')
            if description:
                alt_text = description
            else:
                # Try contextual summary
                contextual_summary = image_block.metadata.get('contextual_summary', '')
                if contextual_summary:
                    alt_text = contextual_summary
        
        # Fallback to existing alt_text or caption
        if not alt_text:
            alt_text = image_block.alt_text or image_block.caption or ""
        
        # Clean up and truncate to 150 words
        if alt_text:
            alt_text = self._clean_alt_text(alt_text)
            return self._truncate_to_words(alt_text, 150)
        return ""
    
    def _wrap_base64_data(self, data: str) -> str:
        """Wrap base64 data at 120 characters for readability."""
        if len(data) <= 120:
            return data
        
        # Show first 50 characters and indicate truncation
        return data[:50] + "..."
    
    def _generate_rich_visual_description(self, image_block: ImageBlock, image_type: str) -> List[str]:
        """Generate rich multi-part visual description following the template."""
        lines = []
        
        # Visual Summary (≤20 sentences)
        visual_summary = self._get_visual_summary(image_block)
        lines.append("**Visual Summary:**")
        lines.append(f"• {visual_summary}")
        lines.append("")
        
        # Key Details (3-30 bullets)
        key_details = self._get_key_details(image_block)
        if key_details:
            lines.append("**Key Details:**")
            for detail in key_details:
                lines.append(f"• {detail}")
            lines.append("")
        
        # Context & Significance (≤1000 words)
        context_significance = self._get_context_significance(image_block)
        if context_significance:
            lines.append("**Context & Significance:**")
            lines.append(context_significance)
            lines.append("")
        
        # Type-specific sections
        if image_type == 'DIAGRAM':
            # Flow Steps for diagrams
            flow_steps = self._get_flow_steps(image_block)
            if flow_steps:
                lines.append("**Flow Steps:**")
                for i, step in enumerate(flow_steps, 1):
                    lines.append(f"{i}. {step}")
                lines.append("")
        else:
            # Data Insights for charts/graphs
            data_insights = self._get_data_insights(image_block)
            if data_insights:
                lines.append("**Data Insights:**")
                for insight in data_insights:
                    lines.append(f"• {insight}")
                lines.append("")
        
        return lines
    
    def _get_visual_summary(self, image_block: ImageBlock) -> str:
        """Get visual summary (≤20 sentences)."""
        if hasattr(image_block, 'metadata') and image_block.metadata:
            # Try contextual summary first
            contextual_summary = image_block.metadata.get('contextual_summary', '')
            if contextual_summary:
                return self._truncate_to_sentences(contextual_summary, 20)
            
            # Try description
            description = image_block.metadata.get('description', '')
            if description:
                return self._truncate_to_sentences(description, 20)
            
            # Try aiAnnotations explanationGenerated
            ai_annotations = image_block.metadata.get('aiAnnotations', {})
            if isinstance(ai_annotations, dict):
                explanation = ai_annotations.get('explanationGenerated', '')
                if explanation:
                    return self._truncate_to_sentences(explanation, 20)
        
        # Return empty if no content available
        return ""
    
    def _get_key_details(self, image_block: ImageBlock) -> List[str]:
        """Get key details (3-30 bullets, ≤100 words each)."""
        details = []
        
        if hasattr(image_block, 'metadata') and image_block.metadata:
            # Get from technical details
            tech_details = image_block.metadata.get('technical_details', {})
            if isinstance(tech_details, dict):
                key_findings = tech_details.get('key_findings', [])
                if key_findings:
                    for finding in key_findings:  # Limit to 30
                        detail = self._truncate_to_words(finding, 100)
                        details.append(detail)
                
                # Add diagram components if available
                components = tech_details.get('diagram_components', [])
                if components:
                    for component in components:  # Limit to 10
                        detail = self._truncate_to_words(f"Component: {component}", 100)
                        details.append(detail)
        
        # Return actual details without minimum requirement
        return details[:30]  # Cap at 30
    
    def _get_context_significance(self, image_block: ImageBlock) -> str:
        """Get context and significance (≤1000 words)."""
        if hasattr(image_block, 'metadata') and image_block.metadata:
            # Check for detailed contextual information
            contextual_summary = image_block.metadata.get('contextual_summary', '')
            if contextual_summary and len(contextual_summary) > 100:
                return self._truncate_to_words(contextual_summary, 1000)
        
        # Generate default context explanation
        # return "This visual element provides important context and supports the document's main content by illustrating key concepts, processes, or data relationships that enhance reader understanding."
        return ""
    
    def _get_flow_steps(self, image_block: ImageBlock) -> List[str]:
        """Get flow steps for diagrams."""
        flow_steps = []
        
        if hasattr(image_block, 'metadata') and image_block.metadata:
            tech_details = image_block.metadata.get('technical_details', {})
            if isinstance(tech_details, dict):
                steps = tech_details.get('flow_steps', [])
                if steps:
                    for step in steps:
                        flow_steps.append(step)
        
        # Return only actual flow steps
        return flow_steps
    
    def _get_data_insights(self, image_block: ImageBlock) -> List[str]:
        """Get data insights for charts/graphs (2-20 bullets)."""
        insights = []
        
        if hasattr(image_block, 'metadata') and image_block.metadata:
            tech_details = image_block.metadata.get('technical_details', {})
            if isinstance(tech_details, dict):
                # Get data points
                data_points = tech_details.get('data_points', [])
                if data_points:
                    for point in data_points:  # Limit to 20
                        insights.append(point)
                
                # Get key findings as insights
                key_findings = tech_details.get('key_findings', [])
                if key_findings:
                    for finding in key_findings:  # Limit to 10
                        insights.append(finding)
        
        # Return only actual insights
        return insights
    
    def _clean_alt_text(self, text: str) -> str:
        """Clean alt text by removing phrases like 'image of', 'picture showing'."""
        # Remove common redundant phrases
        text = re.sub(r'^(image of|picture of|photo of|diagram of|chart of|graph of|figure of)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(showing|depicting|illustrating)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(this is a|this is an|this shows|this depicts)\s+', '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _truncate_text(self, text: str, max_chars: int) -> str:
        """Truncate text to maximum characters."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars-3] + "..."
    
    def _truncate_to_words(self, text: str, max_words: int) -> str:
        """Truncate text to maximum number of words."""
        words = text.split()
        if len(words) <= max_words:
            return text
        return ' '.join(words[:max_words]) + "..."
    
    def _truncate_to_sentences(self, text: str, max_sentences: int) -> str:
        """Truncate text to maximum number of sentences."""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) <= max_sentences:
            return text
        return '. '.join(sentences[:max_sentences]) + "."
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        return len(re.split(r'[.!?]+', text.strip()))
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def _generate_canonical_table(self, table_block: TableBlock, table_number: int) -> str:
        """Generate canonical table format."""
        lines = []
        
        # Table heading
        table_title = table_block.caption or f"Table {table_number}"
        lines.append(f"#### Table {table_number} — {table_title}")
        
        # Generate GitHub-flavored Markdown table
        if table_block.headers and table_block.rows:
            # Headers
            header_line = "| " + " | ".join(self._wrap_cell_content(header) for header in table_block.headers) + " |"
            lines.append(header_line)
            
            # Separator
            separator = "| " + " | ".join("---" for _ in table_block.headers) + " |"
            lines.append(separator)
            
            # Rows
            for row in table_block.rows:
                # Ensure row has same number of columns as headers
                padded_row = row + [""] * (len(table_block.headers) - len(row))
                padded_row = padded_row[:len(table_block.headers)]
                
                row_line = "| " + " | ".join(self._wrap_cell_content(str(cell)) for cell in padded_row) + " |"
                lines.append(row_line)
        
        # Table Summary
        lines.append("")
        summary = self._generate_table_summary(table_block)
        lines.append(f"> **Table Summary:** {summary}")
        
        return "\n".join(lines)
    
    def _wrap_cell_content(self, content: str) -> str:
        """Wrap cell content at word boundaries if >80 chars."""
        if len(content) <= 80:
            return content
        
        # Simple word wrapping for table cells
        words = content.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= 80:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return "<br>".join(lines)
    
    def _generate_table_summary(self, table_block: TableBlock) -> str:
        """Generate table summary with key takeaways."""
        takeaways = []
        
        # Basic stats
        if table_block.headers and table_block.rows:
            takeaways.append(f"{len(table_block.rows)} rows of data with {len(table_block.headers)} columns")
        
        # Try to extract meaningful insights
        if hasattr(table_block, 'metadata') and table_block.metadata:
            summary = table_block.metadata.get('summary', '')
            if summary:
                takeaways.append(summary)
        
        return "; ".join(takeaways) if takeaways else "Table presents structured data and information."

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
