import pytest
import asyncio
import base64
from io import BytesIO
from PIL import Image
from unittest.mock import patch, AsyncMock, MagicMock

from backend.app.parsers.ai_processor import AIProcessor
from backend.app.parsers.ast_models import DocumentAST, ImageBlock, TableBlock, MathBlock
from backend.app.core.config import settings

@pytest.fixture
def ai_processor():
    return AIProcessor()

@pytest.fixture
def mock_ai_service():
    service = MagicMock()
    service.analyze_image_structured = AsyncMock(return_value={
        "description": "Mocked image description",
        "aiAnnotations": {"ocrText": "Mocked OCR text"}
    })
    return service

@pytest.fixture
def sample_image_block():
    # Create a tiny base64 PNG for testing
    img = Image.new('RGB', (10, 10), color='blue')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return ImageBlock(data=img_str, format="PNG", alt_text="Original alt text")

@pytest.mark.asyncio
async def test_process_ast_with_images_and_table_extraction_enabled(
    ai_processor: AIProcessor,
    mock_ai_service: MagicMock,
    sample_image_block: ImageBlock
):
    settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED = True
    settings.AI_PROCESSOR_IMAGE_BATCH_SIZE = 1 # Test with batch size 1 for simplicity

    ast = DocumentAST(images=[sample_image_block, sample_image_block]) # Two images

    mock_extracted_table = TableBlock(headers=["H1"], rows=[["C1"]])

    with patch('backend.app.parsers.ai_processor.get_ai_service', AsyncMock(return_value=mock_ai_service)) as mock_get_service, \
         patch('backend.app.parsers.ai_processor.extract_table_from_pil_image', AsyncMock(return_value=mock_extracted_table)) as mock_extract_table:

        processed_ast = await ai_processor.process_ast(ast)

        assert mock_get_service.called # AIService should have been fetched

        # Check descriptions (called for each image)
        assert mock_ai_service.analyze_image_structured.call_count == 2
        for img_block in processed_ast.images:
            assert "Mocked image description" in img_block.alt_text

        # Check table extraction (called for each image)
        assert mock_extract_table.call_count == 2
        assert len(processed_ast.tables) == 2
        for table in processed_ast.tables:
            assert table.headers == ["H1"]

@pytest.mark.asyncio
async def test_process_ast_with_images_and_table_extraction_disabled(
    ai_processor: AIProcessor,
    mock_ai_service: MagicMock,
    sample_image_block: ImageBlock
):
    settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED = False # Disable feature

    ast = DocumentAST(images=[sample_image_block])

    with patch('backend.app.parsers.ai_processor.get_ai_service', AsyncMock(return_value=mock_ai_service)) as mock_get_service, \
         patch('backend.app.parsers.ai_processor.extract_table_from_pil_image', AsyncMock()) as mock_extract_table:

        processed_ast = await ai_processor.process_ast(ast)

        assert mock_get_service.called
        assert mock_ai_service.analyze_image_structured.call_count == 1
        assert "Mocked image description" in processed_ast.images[0].alt_text

        mock_extract_table.assert_not_called() # Should not be called
        assert len(processed_ast.tables) == 0

@pytest.mark.asyncio
async def test_process_ast_no_images(ai_processor: AIProcessor):
    ast = DocumentAST() # No images, no math

    with patch('backend.app.parsers.ai_processor.get_ai_service', AsyncMock()) as mock_get_service, \
         patch('backend.app.parsers.ai_processor.extract_table_from_pil_image', AsyncMock()) as mock_extract_table:

        processed_ast = await ai_processor.process_ast(ast)

        mock_get_service.assert_not_called()
        mock_extract_table.assert_not_called()
        assert len(processed_ast.tables) == 0
        assert len(processed_ast.images) == 0

@pytest.mark.asyncio
async def test_process_ast_image_description_failure(
    ai_processor: AIProcessor,
    mock_ai_service: MagicMock,
    sample_image_block: ImageBlock
):
    settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED = True
    mock_ai_service.analyze_image_structured.side_effect = Exception("Describe API failed")

    ast = DocumentAST(images=[sample_image_block])
    mock_extracted_table = TableBlock(headers=["H1"], rows=[["C1"]])

    with patch('backend.app.parsers.ai_processor.get_ai_service', AsyncMock(return_value=mock_ai_service)), \
         patch('backend.app.parsers.ai_processor.extract_table_from_pil_image', AsyncMock(return_value=mock_extracted_table)) as mock_extract_table:

        processed_ast = await ai_processor.process_ast(ast)

        assert "Image (description failed)" in processed_ast.images[0].alt_text
        assert mock_extract_table.call_count == 1 # Table extraction should still run
        assert len(processed_ast.tables) == 1

@pytest.mark.asyncio
async def test_process_ast_table_extraction_failure(
    ai_processor: AIProcessor,
    mock_ai_service: MagicMock,
    sample_image_block: ImageBlock
):
    settings.EXTRACT_TABLES_FROM_IMAGES_ENABLED = True
    ast = DocumentAST(images=[sample_image_block])

    with patch('backend.app.parsers.ai_processor.get_ai_service', AsyncMock(return_value=mock_ai_service)), \
         patch('backend.app.parsers.ai_processor.extract_table_from_pil_image', AsyncMock(side_effect=Exception("Table extraction failed"))) as mock_extract_table:

        processed_ast = await ai_processor.process_ast(ast)

        assert "Mocked image description" in processed_ast.images[0].alt_text # Description should work
        assert mock_extract_table.call_count == 1
        assert len(processed_ast.tables) == 0 # No table added

@pytest.mark.asyncio
async def test_process_math_blocks(ai_processor: AIProcessor):
    # Basic test to ensure math processing is called, though it's a placeholder
    math_block = MathBlock(content="x=1", format="text")
    ast = DocumentAST(math=[math_block])

    processed_ast = await ai_processor.process_ast(ast)
    assert len(processed_ast.math) == 1
    assert processed_ast.math[0].format == "latex" # Check simple conversion

# TODO: Add tests for progress callback if its output is critical to verify.
# Testing asyncio.gather and batching behavior in detail might require more intricate mocks
# or observing call orders/timing, which can be complex for unit tests.
# The current tests verify that the core functions are called the expected number of times
# based on the number of images and settings.
