#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_backend():
    """Test basic backend functionality"""
    print("🔄 Testing backend imports...")
    
    try:
        from backend.app.main import app
        print("✅ FastAPI app imported successfully")
        
        from backend.app.core.config import get_settings
        settings = get_settings()
        print(f"✅ Settings loaded: debug={settings.debug}, host={settings.host}, port={settings.port}")
        
        from backend.app.services.ai_service import get_ai_service
        ai_service = await get_ai_service()
        print("✅ AI service initialized")
        
        # Test health check
        health_status = await ai_service.health_check()
        print(f"✅ AI service health check: {health_status['status']}")
        
        from backend.app.parsers.parser_factory import ParserFactory
        parser_factory = ParserFactory()
        supported_extensions = parser_factory.get_supported_extensions()
        print(f"✅ Parser factory loaded. Supported extensions: {supported_extensions}")
        
        print("\n🎉 Backend is fully functional!")
        print(f"📋 Supported file types: {', '.join(supported_extensions)}")
        print(f"🌐 Server configured for: {settings.host}:{settings.port}")
        print(f"🔧 Debug mode: {settings.debug}")
        print(f"🤖 AI service status: {health_status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_backend())
    sys.exit(0 if result else 1)
