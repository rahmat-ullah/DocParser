import pytest
import asyncio
from pathlib import Path

from app.parsers.txt_parser import TXTParser

@pytest.fixture
def txt_parser():
    return TXTParser()

@pytest.fixture
def txt_file(tmp_path):
    # Create a simple TXT file with content
    content = """# Main Heading

This is a regular paragraph with some text.

## Subheading

- List item 1
- List item 2

    This is code block

> This is a quote

Another paragraph here."""
    
    path = tmp_path / "test.txt"
    path.write_text(content, encoding='utf-8')
    return path

@pytest.mark.asyncio
async def test_txt_parser_supports_file(txt_parser, txt_file):
    assert txt_parser.supports_file(txt_file) == True
    
@pytest.mark.asyncio
async def test_txt_parser_parse(txt_parser, txt_file):
    result = await txt_parser.parse_to_dict(txt_file)
    assert isinstance(result, dict)
    assert "metadata" in result
    assert result["metadata"]["format"] == "TXT"
    assert "textBlocks" in result
    assert len(result["textBlocks"]) > 0
    
    
    # Check if headings were detected
    headings = [block for block in result["textBlocks"] if block["type"] == "heading"]
    assert len(headings) >= 2
    
    # Check if list items were detected
    list_items = [block for block in result["textBlocks"] if block["type"] == "list_item"]
    assert len(list_items) >= 2
    
    # Check if paragraphs were detected
    paragraphs = [block for block in result["textBlocks"] if block["type"] == "paragraph"]
    assert len(paragraphs) >= 1
    
    # Check if quote was detected
    quotes = [block for block in result["textBlocks"] if block["type"] == "quote"]
    assert len(quotes) >= 1
