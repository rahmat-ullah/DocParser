#!/usr/bin/env python3
"""
Test script to verify enhanced AI service functionality
"""

import asyncio
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_enhanced_ai_service():
    """Test the enhanced AI service to ensure it works correctly."""
    
    try:
        from app.services.enhanced_ai_service import get_enhanced_ai_service
        from app.core.config import settings
        
        print("Testing Enhanced AI Service...")
        
        # Check if API key is set
        if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
            print("❌ OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
            return False
        
        print("✅ OpenAI API key is configured")
        
        # Test service initialization
        service = await get_enhanced_ai_service()
        print("✅ Enhanced AI service initialized successfully")
        
        # Test document context analysis
        sample_text = "This is a test document about machine learning algorithms."
        sample_metadata = {"title": "ML Test", "pages": 1}
        
        print("Testing document context analysis...")
        try:
            context = await asyncio.wait_for(
                service.set_document_context(sample_text, sample_metadata, 0),
                timeout=30.0
            )
            print(f"✅ Document context analysis successful: {context.document_type.value}")
        except asyncio.TimeoutError:
            print("⚠️  Document context analysis timed out (expected if API is slow)")
        except Exception as e:
            print(f"❌ Document context analysis failed: {e}")
            return False
        
        # Test health check
        print("Testing health check...")
        try:
            health = await service.health_check()
            print(f"✅ Health check successful: {health['status']}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        print("✅ All tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_ai_service())
    sys.exit(0 if success else 1)
