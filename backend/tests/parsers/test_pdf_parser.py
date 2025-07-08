import pytest
import asyncio
from pathlib import Path

from app.parsers.pdf_parser import PDFParser

@pytest.fixture
def pdf_parser():
    return PDFParser()

@pytest.fixture
def pdf_file(tmp_path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    path = tmp_path / "test.pdf"
    
    # Create a simple PDF with reportlab
    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(100, 750, "Test PDF Document")
    c.drawString(100, 730, "This is a test paragraph.")
    c.save()
    
    return path
    
@pytest.mark.asyncio
async def test_pdf_parser_supports_file(pdf_parser):
    from pathlib import Path
    test_file = Path("test.pdf")
    assert pdf_parser.supports_file(test_file) == True
    
@pytest.mark.asyncio
async def test_pdf_parser_parse(pdf_parser, pdf_file):
    result = await pdf_parser.parse_to_dict(pdf_file)
    assert isinstance(result, dict)
    assert "metadata" in result
    assert result["metadata"]["format"] == "PDF"
    assert "textBlocks" in result
    # Should extract at least some text from our simple PDF
    assert len(result["textBlocks"]) >= 1
