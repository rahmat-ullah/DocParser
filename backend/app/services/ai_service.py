"""
AI service abstraction for OpenAI Vision API.
Provides image description functionality with retry logic and OCR fallback.
"""

import asyncio
import base64
import logging
from typing import Optional, Dict, Any
from io import BytesIO

import httpx
from openai import AsyncOpenAI
from PIL import Image
import pytesseract

from app.core.config import get_openai_config


logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class VisionAPIError(AIServiceError):
    """Error specific to Vision API calls."""
    pass


class OCRError(AIServiceError):
    """Error specific to OCR operations."""
    pass


class AIService:
    """
    AI service abstraction for OpenAI Vision API.
    
    Provides image description functionality with automatic retry logic
    and optional OCR fallback when Vision API fails.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI service.
        
        Args:
            config: Optional configuration dictionary. If None, uses default config.
        """
        self.config = config or get_openai_config()
        self.client = AsyncOpenAI(
            api_key=self.config["api_key"],
            timeout=self.config["timeout"]
        )
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        api_key = self.config.get("api_key", "")
        if not api_key or api_key == "your_openai_api_key_here":
            logger.warning("OpenAI API key not configured. AI features will be limited.")
            # Don't raise error for development
        
        if not self.config.get("vision_model"):
            raise AIServiceError("Vision model is required")
        
        if self.config.get("max_retries", 0) < 0:
            raise AIServiceError("Max retries must be non-negative")
        
        if self.config.get("retry_delay", 0) <= 0:
            raise AIServiceError("Retry delay must be positive")
    
    async def describe_image(self, base64_img: str) -> str:
        """
        Describe an image using OpenAI Vision API.
        
        Args:
            base64_img: Base64-encoded image string
            
        Returns:
            String description of the image
            
        Raises:
            AIServiceError: If the operation fails after all retries
        """
        # Validate input
        if not base64_img:
            raise AIServiceError("Base64 image string is required")
        
        # Try Vision API first
        try:
            return await self._describe_with_vision_api(base64_img)
        except VisionAPIError as e:
            logger.warning(f"Vision API failed: {e}")
            
            # Fall back to OCR if enabled
            if self.config.get("ocr_fallback_enabled", True):
                logger.info("Falling back to OCR")
                try:
                    return await self._describe_with_ocr(base64_img)
                except OCRError as ocr_error:
                    logger.error(f"OCR fallback failed: {ocr_error}")
                    raise AIServiceError(f"Both Vision API and OCR failed. Vision API: {e}, OCR: {ocr_error}")
            else:
                raise AIServiceError(f"Vision API failed and OCR fallback is disabled: {e}")
    
    async def _describe_with_vision_api(self, base64_img: str) -> str:
        """
        Describe image using OpenAI Vision API with retry logic.
        
        Args:
            base64_img: Base64-encoded image string
            
        Returns:
            String description of the image
            
        Raises:
            VisionAPIError: If the API call fails after all retries
        """
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 1.0)
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.config["vision_model"],
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Describe this image in detail. Focus on any text, tables, charts, or important visual elements that might be relevant for document processing."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_img}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                
                if not response.choices:
                    raise VisionAPIError("No response from Vision API")
                
                content = response.choices[0].message.content
                if not content:
                    raise VisionAPIError("Empty response from Vision API")
                
                return content.strip()
                
            except Exception as e:
                if attempt == max_retries:
                    raise VisionAPIError(f"Vision API failed after {max_retries + 1} attempts: {e}")
                
                logger.warning(f"Vision API attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                
                # Exponential backoff
                retry_delay *= 2
        
        raise VisionAPIError("Unexpected error in Vision API retry logic")
    
    async def _describe_with_ocr(self, base64_img: str) -> str:
        """
        Extract text from image using OCR as fallback.
        
        Args:
            base64_img: Base64-encoded image string
            
        Returns:
            Extracted text from the image
            
        Raises:
            OCRError: If OCR extraction fails
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_img)
            image = Image.open(BytesIO(image_data))
            
            # Configure tesseract if path is provided
            if self.config.get("tesseract_path"):
                pytesseract.pytesseract.tesseract_cmd = self.config["tesseract_path"]
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                raise OCRError("No text extracted from image")
            
            return f"OCR Extracted Text: {text.strip()}"
            
        except Exception as e:
            raise OCRError(f"OCR extraction failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the AI service.
        
        Returns:
            Dictionary containing health status information
        """
        status = {
            "service": "ai_service",
            "status": "healthy",
            "checks": {}
        }
        
        # Check OpenAI API connectivity
        api_key = self.config.get("api_key", "")
        if not api_key or api_key == "your_openai_api_key_here":
            status["checks"]["openai_api"] = {
                "status": "not_configured",
                "message": "OpenAI API key not configured"
            }
        else:
            try:
                # Simple API call to check connectivity
                response = await self.client.models.list()
                status["checks"]["openai_api"] = {
                    "status": "healthy",
                    "message": "API connection successful"
                }
            except Exception as e:
                status["status"] = "unhealthy"
                status["checks"]["openai_api"] = {
                    "status": "unhealthy",
                    "message": f"API connection failed: {e}"
                }
        
        # Check OCR availability if enabled
        if self.config.get("ocr_fallback_enabled", True):
            try:
                # Create a simple test image
                test_image = Image.new('RGB', (100, 30), color='white')
                
                if self.config.get("tesseract_path"):
                    pytesseract.pytesseract.tesseract_cmd = self.config["tesseract_path"]
                
                # Test OCR
                pytesseract.image_to_string(test_image)
                status["checks"]["ocr"] = {
                    "status": "healthy",
                    "message": "OCR available"
                }
            except Exception as e:
                status["checks"]["ocr"] = {
                    "status": "unhealthy",
                    "message": f"OCR unavailable: {e}"
                }
        else:
            status["checks"]["ocr"] = {
                "status": "disabled",
                "message": "OCR fallback disabled"
            }
        
        return status
    
    async def close(self) -> None:
        """Close the AI service and cleanup resources."""
        await self.client.close()


# Global service instance
_ai_service: Optional[AIService] = None


async def get_ai_service() -> AIService:
    """
    Get or create the global AI service instance.
    
    Returns:
        AIService instance
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


async def shutdown_ai_service() -> None:
    """Shutdown the global AI service instance."""
    global _ai_service
    if _ai_service is not None:
        await _ai_service.close()
        _ai_service = None
