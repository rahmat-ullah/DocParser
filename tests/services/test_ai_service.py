"""
Unit tests for AIService class in ai_service.py
Uses respx and httpx for mocking HTTP requests
"""

import asyncio
import base64
import pytest
import respx
from httpx import AsyncClient

from app.services.ai_service import AIService, AIServiceError, VisionAPIError, OCRError


@pytest.fixture
async def ai_service():
    """Fixture for initializing AIService instance for testing."""
    service = AIService()
    try:
        yield service
    finally:
        await service.close()


@respx.mock
@pytest.mark.asyncio
async def test_describe_image_with_vision_api(mocked_respx, ai_service: AIService):
    """
    Test describe_image method using Vision API.
    Mocked response simulates successful API call
    """
    # Mock Vision API endpoint with success response
    api_url = "https://api.openai.com/v1/chat/completions"
    mocked_respx.post(api_url).mock(return_value=httpx.Response(200, json={
        "choices": [{
            "message": {"content": "Mocked description of the image using Vision API."}
        }],
        "usage": {}
    }))
    
    # Base64 encode a mock image
    mock_image_data = base64.b64encode(b"mock image data").decode('ascii')
    
    # Call describe_image
    description = await ai_service.describe_image(mock_image_data)
    
    # Verify result
    assert description == "Mocked description of the image using Vision API."


@respx.mock
@pytest.mark.asyncio
async def test_describe_image_with_ocr_fallback(mocked_respx, ai_service: AIService):
    """
    Test OCR fallback of describe_image method when Vision API fails.
    """
    # Mock Vision API endpoint with failure response
    api_url = "https://api.openai.com/v1/conversations"
    mocked_respx.post(api_url).mock(return_value=httpx.Response(500))
    
    # Base64 encode a mock image
    mock_image_data = base64.b64encode(b"mock image data").decode('ascii')
    
    # Call describe_image
    description = await ai_service.describe_image(mock_image_data)
    
    # Verify OCR fallback was used
    assert description.startswith("OCR Extracted Text:")


@respx.mock
@pytest.mark.asyncio
async def test_describe_image_both_methods_fail(mocked_respx, ai_service: AIService):
    """
    Test both Vision API and OCR fallback fail in describe_image
    """
    # Mock Vision API endpoint and failed responses
    api_url = "https://api.openai.com/v1/conversations"
    mocked_respx.post(api_url).mock(return_value=httpx.Response(500))
    
    # Configure OCR to also fail by passing invalid image data
    ai_service.config["ocr_fallback_enabled"] = True
    mock_image_data = "invalid_base64"
    
    # Call describe_image and expect AIServiceError
    with pytest.raises(AIServiceError) as exc_info:
        await ai_service.describe_image(mock_image_data)
    
    # Verify Exception
    assert "Both Vision API and OCR failed" in str(exc_info.value)
