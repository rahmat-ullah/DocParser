import pytest
import asyncio
from pathlib import Path
from PIL import Image
from unittest.mock import patch, AsyncMock

from backend.app.parsers.img_parser import IMGParser # Corrected import path
from backend.app.parsers.ast_models import TableBlock
from backend.app.core.config import settings

# Fixtures
@pytest.fixture
def img_parser():
    # Ensure settings are loaded for the parser, especially for API keys
    # In a real test setup, you might override settings for testing
    if not settings.OPENAI_API_KEY:
        settings.OPENAI_API_KEY = "fake_test_key" # Ensure key exists for parser init
    return IMGParser()

@pytest.fixture
def simple_image_file(tmp_path: Path) -> Path:
    img = Image.new('RGB', (100, 100), color='red')
    path = tmp_path / "test_simple.png"
    img.save(path)
    return path

@pytest.fixture
def sample_table_image_path() -> Path:
    # Assumes the image is in backend/tests/fixtures/
    # Adjust path if running tests from a different root
    base_path = Path(__file__).parent.parent # Should be backend/tests/
    return base_path / "fixtures" / "sample_table_image.png"

# Basic Tests (similar to original)
@pytest.mark.asyncio
async def test_img_parser_supports_file(img_parser: IMGParser, simple_image_file: Path):
    assert img_parser.supports_file(simple_image_file) is True
    assert img_parser.supports_file(Path("test.txt")) is False

@pytest.mark.asyncio
async def test_img_parser_parse_simple_image(img_parser: IMGParser, simple_image_file: Path):
    # Test parsing of a simple image without table content, mock external calls
    with patch('pytesseract.image_to_string', return_value="No table here") as mock_ocr, \
         patch('openai.chat.completions.create', new_callable=AsyncMock) as mock_openai:

        mock_openai.return_value.choices = [AsyncMock(message=AsyncMock(content="No table found"))]

        ast = await img_parser.parse(simple_image_file)

        assert ast.metadata["format"] == "IMAGE"
        assert ast.metadata["image_format"] == "PNG"
        assert ast.metadata["width"] == 100
        assert ast.metadata["height"] == 100
        assert len(ast.images) == 1
        assert len(ast.tables) == 0 # Expect no tables

        mock_ocr.assert_called_once()
        mock_openai.assert_called_once()

# Table Extraction Tests
@pytest.mark.asyncio
async def test_img_parser_extracts_table_successfully(img_parser: IMGParser, sample_table_image_path: Path):
    if not sample_table_image_path.exists():
        pytest.skip("Sample table image not found, skipping test.")

    # Mock Tesseract to return some text that implies a table
    # Actual Tesseract output for sample_table_image.png is complex, so simplify for mock
    mock_ocr_text = """
    Name    Age   City
    Alice   30    New York
    Bob     24    Paris
    Charlie 45    London
    """
    # Mock OpenAI to return a valid Markdown table
    mock_markdown_table = """
    | Name    | Age | City     |
    |---------|-----|----------|
    | Alice   | 30  | New York |
    | Bob     | 24  | Paris    |
    | Charlie | 45  | London   |
    """

    with patch('pytesseract.image_to_string', return_value=mock_ocr_text) as mock_ocr, \
         patch('openai.chat.completions.create', new_callable=AsyncMock) as mock_openai:

        mock_openai.return_value.choices = [AsyncMock(message=AsyncMock(content=mock_markdown_table))]

        ast = await img_parser.parse(sample_table_image_path)

        mock_ocr.assert_called_once()
        # Ensure the image passed to pytesseract is a PIL Image (or handle filename if that's what your impl uses)
        # args, _ = mock_ocr.call_args
        # assert isinstance(args[0], Image.Image)

        mock_openai.assert_called_once()
        # You could inspect mock_openai.call_args to check the prompt if needed

        assert len(ast.tables) == 1
        table = ast.tables[0]
        assert isinstance(table, TableBlock)
        assert table.headers == ["Name", "Age", "City"]
        assert table.rows == [
            ["Alice", "30", "New York"],
            ["Bob", "24", "Paris"],
            ["Charlie", "45", "London"]
        ]
        assert "Table from sample_table_image.png" in table.caption # Check caption

@pytest.mark.asyncio
async def test_img_parser_handles_no_table_found(img_parser: IMGParser, sample_table_image_path: Path):
    if not sample_table_image_path.exists():
        pytest.skip("Sample table image not found, skipping test.")

    mock_ocr_text = "Some random text without any tabular structure."

    with patch('pytesseract.image_to_string', return_value=mock_ocr_text) as mock_ocr, \
         patch('openai.chat.completions.create', new_callable=AsyncMock) as mock_openai:

        mock_openai.return_value.choices = [AsyncMock(message=AsyncMock(content="No table found"))]

        ast = await img_parser.parse(sample_table_image_path)

        mock_ocr.assert_called_once()
        mock_openai.assert_called_once()

        assert len(ast.tables) == 0

@pytest.mark.asyncio
async def test_img_parser_handles_ocr_failure(img_parser: IMGParser, simple_image_file: Path):
    with patch('pytesseract.image_to_string', side_effect=Exception("OCR Failed")) as mock_ocr, \
         patch('openai.chat.completions.create', new_callable=AsyncMock) as mock_openai:

        # Even if OCR fails, basic image parsing should proceed.
        # The _extract_table_from_image_data method should catch the error and return None.
        ast = await img_parser.parse(simple_image_file)

        mock_ocr.assert_called_once()
        mock_openai.assert_not_called() # OpenAI should not be called if OCR fails

        assert len(ast.images) == 1 # Basic image info should still be there
        assert len(ast.tables) == 0

@pytest.mark.asyncio
async def test_img_parser_handles_openai_api_error(img_parser: IMGParser, sample_table_image_path: Path):
    if not sample_table_image_path.exists():
        pytest.skip("Sample table image not found, skipping test.")

    mock_ocr_text = "Some text that might contain a table."

    # Simulate an API error from OpenAI
    from openai import APIError # Make sure to import specific error type if needed
    
    with patch('pytesseract.image_to_string', return_value=mock_ocr_text) as mock_ocr, \
         patch('openai.chat.completions.create', new_callable=AsyncMock, side_effect=APIError("Simulated API Error", response=None, body=None)) as mock_openai:

        ast = await img_parser.parse(sample_table_image_path)

        mock_ocr.assert_called_once()
        mock_openai.assert_called_once()

        assert len(ast.images) == 1 # Basic image info should still be there
        assert len(ast.tables) == 0 # No table should be extracted on API error

@pytest.mark.asyncio
async def test_img_parser_no_openai_key(img_parser: IMGParser, simple_image_file: Path):
    original_key = settings.OPENAI_API_KEY
    settings.OPENAI_API_KEY = "" # Temporarily unset API key
    
    # Reset the api_key on the openai module if it was set by parser's __init__
    # This is a bit tricky as the key might be set on the global openai client.
    # A cleaner way would be to inject the openai client or settings into the parser.
    with patch('openai.api_key', new_callable=lambda: None), \
         patch('pytesseract.image_to_string', return_value="Some text") as mock_ocr, \
         patch('openai.chat.completions.create', new_callable=AsyncMock) as mock_openai:

        # Re-initialize parser to pick up changed settings if necessary
        # This depends on how IMGParser sets the API key.
        # For this test, assume the check in _extract_table_from_image_data is effective.
        parser_no_key = IMGParser()

        ast = await parser_no_key.parse(simple_image_file)

        assert len(ast.images) == 1
        assert len(ast.tables) == 0
        # OCR is called before API key check for table extraction part in current IMGParser impl
        mock_ocr.assert_called_once()
        mock_openai.assert_not_called() # This is the key check

    settings.OPENAI_API_KEY = original_key # Restore key

# It might also be useful to test the markdown_utils.parse_markdown_table_to_table_block separately
# in its own test file, e.g., backend/tests/utils/test_markdown_utils.py
# For brevity, not adding those here but it's good practice.
