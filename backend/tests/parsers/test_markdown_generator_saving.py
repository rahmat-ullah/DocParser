"""
Unit tests for MarkdownGenerator saving logic.
Tests the integration of MarkdownGenerator with file saving functionality.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.parsers.markdown_generator import MarkdownGenerator
from app.parsers.ast_models import (
    DocumentAST, TextBlock, ImageBlock, TableBlock, 
    MathBlock, BlockType
)
from app.utils.storage import save_markdown, get_markdown_path
from app.services.document_processor import DocumentProcessor
from app.core.config import settings


class TestMarkdownGeneratorSaving:
    """Test cases for MarkdownGenerator saving functionality."""
    
    @pytest.fixture
    def sample_ast(self):
        """Create a sample DocumentAST for testing."""
        return DocumentAST(
            metadata={
                "title": "Test Document",
                "author": "Test Author",
                "format": "pdf",
                "pages": 5
            },
            textBlocks=[
                TextBlock(
                    content="Main Heading",
                    type=BlockType.HEADING,
                    level=1,
                    page=1,
                    bbox=[0, 0, 100, 20]
                ),
                TextBlock(
                    content="This is a paragraph of text.",
                    type=BlockType.PARAGRAPH,
                    page=1,
                    bbox=[0, 30, 100, 50]
                ),
                TextBlock(
                    content="print('Hello, world!')",
                    type=BlockType.CODE,
                    page=1,
                    bbox=[0, 60, 100, 80]
                )
            ],
            images=[
                ImageBlock(
                    data="base64_image_data_here",
                    format="PNG",
                    alt_text="Test image",
                    caption="Figure 1: Test diagram",
                    page=1,
                    bbox=[0, 90, 100, 190]
                )
            ],
            tables=[
                TableBlock(
                    headers=["Column 1", "Column 2", "Column 3"],
                    rows=[
                        ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                        ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
                    ],
                    caption="Table 1: Sample data",
                    page=2,
                    bbox=[0, 0, 100, 50]
                )
            ],
            math=[
                MathBlock(
                    content="E = mc^2",
                    format="latex",
                    is_inline=False,
                    page=2,
                    bbox=[0, 60, 100, 80]
                )
            ]
        )
    
    @pytest.fixture
    def markdown_generator(self):
        """Create a MarkdownGenerator instance."""
        return MarkdownGenerator()
    
    def test_markdown_generation_content(self, markdown_generator, sample_ast):
        """Test that markdown content is generated correctly."""
        markdown_content = markdown_generator.generate(sample_ast)
        
        # Check frontmatter
        assert "---" in markdown_content
        assert "title: Test Document" in markdown_content
        assert "author: Test Author" in markdown_content
        assert "format: pdf" in markdown_content
        assert "pages: 5" in markdown_content
        
        # Check content sections
        assert "# Main Heading" in markdown_content
        assert "This is a paragraph of text." in markdown_content
        assert "```\nprint('Hello, world!')\n```" in markdown_content
        
        # Check image
        assert "![Test image]" in markdown_content
        assert "*Figure 1: Test diagram*" in markdown_content
        
        # Check table
        assert "| Column 1 | Column 2 | Column 3 |" in markdown_content
        assert "| Row 1 Col 1 | Row 1 Col 2 | Row 1 Col 3 |" in markdown_content
        
        # Check math
        assert "$$\nE = mc^2\n$$" in markdown_content
    
    def test_save_markdown_creates_directory(self):
        """Test that save_markdown creates the directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with non-existent subdirectory
            file_path = os.path.join(temp_dir, "subdir", "test.md")
            content = "# Test Content\n\nThis is a test."
            
            # Save the markdown
            save_markdown(content, file_path)
            
            # Check that file was created
            assert os.path.exists(file_path)
            
            # Check content
            with open(file_path, 'r') as f:
                assert f.read() == content
    
    def test_save_markdown_overwrites_existing(self):
        """Test that save_markdown overwrites existing files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Old content")
            temp_path = f.name
        
        try:
            new_content = "# New Content\n\nThis is new."
            save_markdown(new_content, temp_path)
            
            with open(temp_path, 'r') as f:
                assert f.read() == new_content
        finally:
            os.unlink(temp_path)
    
    def test_get_markdown_path_format(self):
        """Test that get_markdown_path generates correct file paths."""
        document_id = "doc123"
        original_name = "My Document.pdf"
        
        path = get_markdown_path(document_id, original_name)
        
        # Check path components
        assert "markdown_storage" in path
        assert document_id in path
        assert "My_Document.pdf.md" in path
        assert " " not in path  # Spaces should be replaced
    
    @pytest.mark.asyncio
    async def test_document_processor_saves_markdown(self, sample_ast):
        """Test that DocumentProcessor correctly saves markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock settings to use temp directory
            with patch.object(settings, 'markdown_dir', temp_dir):
                processor = DocumentProcessor()
                
                # Mock the parser to return our sample AST
                mock_parser = Mock()
                mock_parser.parse = Mock(return_value=sample_ast)
                
                with patch.object(processor.parser_factory, 'get_parser', return_value=mock_parser):
                    # Process a fake document
                    document_id = "test123"
                    file_path = Path("test_document.pdf")
                    
                    # Collect progress updates
                    progress_updates = []
                    async for progress in processor.process_document(
                        file_path, 
                        document_id, 
                        enable_ai_processing=False
                    ):
                        progress_updates.append(progress)
                    
                    # Check that markdown was saved
                    expected_path = Path(temp_dir) / document_id / "test_document.md"
                    assert expected_path.exists()
                    
                    # Check the content
                    content = expected_path.read_text(encoding="utf-8")
                    assert "# Main Heading" in content
                    assert "This is a paragraph of text." in content
                    
                    # Check that the path is returned in completion details
                    completion = progress_updates[-1]
                    assert completion.stage == "completion"
                    assert "markdown_path" in completion.details
                    assert str(expected_path) == completion.details["markdown_path"]
    
    def test_markdown_generator_empty_ast(self, markdown_generator):
        """Test markdown generation with empty AST."""
        empty_ast = DocumentAST(
            metadata={},
            textBlocks=[],
            images=[],
            tables=[],
            math=[]
        )
        
        content = markdown_generator.generate(empty_ast)
        assert content == ""  # Should return empty string for empty document
    
    def test_markdown_generator_special_characters(self, markdown_generator):
        """Test markdown generation with special characters."""
        ast = DocumentAST(
            metadata={"title": "Test & <Special> \"Characters\""},
            textBlocks=[
                TextBlock(
                    content="Text with * asterisks and _ underscores",
                    type=BlockType.PARAGRAPH,
                    page=1,
                    bbox=[0, 0, 100, 20]
                ),
                TextBlock(
                    content="Code with `backticks` and $dollars$",
                    type=BlockType.CODE,
                    page=1,
                    bbox=[0, 30, 100, 50]
                )
            ],
            images=[],
            tables=[],
            math=[]
        )
        
        content = markdown_generator.generate(ast)
        
        # Check that special characters are preserved
        assert "Test & <Special> \"Characters\"" in content
        assert "Text with * asterisks and _ underscores" in content
        assert "Code with `backticks` and $dollars$" in content
    
    def test_markdown_path_persistence(self):
        """Test that markdown file paths are consistent and predictable."""
        doc_id = "consistent123"
        original_name = "Test Document.pdf"
        
        # Generate path multiple times
        path1 = get_markdown_path(doc_id, original_name)
        path2 = get_markdown_path(doc_id, original_name)
        
        # Should be identical
        assert path1 == path2
        
        # Should handle different extensions
        path_docx = get_markdown_path(doc_id, "Test Document.docx")
        assert path_docx != path1
        assert ".docx.md" in path_docx
