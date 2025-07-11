#!/usr/bin/env python3
"""
Test script to validate Socket.IO implementation.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_socketio_imports():
    """Test that Socket.IO components can be imported correctly."""
    try:
        from app.socketio import (
            sio, 
            socket_app, 
            mount_socketio,
            emit_progress,
            emit_status,
            emit_error,
            get_active_connections
        )
        print("✓ Socket.IO imports successful")
        
        from app.services.progress_emitter import (
            ProgressEmitter,
            emit_document_progress
        )
        print("✓ Progress emitter imports successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

async def test_progress_emitter():
    """Test progress emitter functionality."""
    try:
        from app.services.progress_emitter import ProgressEmitter
        from app.parsers.ast_models import ParseProgress
        
        # Create a progress emitter
        emitter = ProgressEmitter()
        
        # Create a test progress object
        progress = ParseProgress(
            stage="testing",
            progress=0.5,
            message="Test progress message",
            details={"test": True}
        )
        
        # This should not fail (though it won't actually emit without active connections)
        result = await emitter.emit_progress("test-doc-id", progress)
        print(f"✓ Progress emitter test completed (result: {result})")
        
        return True
        
    except Exception as e:
        print(f"✗ Progress emitter test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("Testing Socket.IO implementation...")
    print("=" * 50)
    
    # Test imports
    imports_ok = await test_socketio_imports()
    
    # Test progress emitter
    emitter_ok = await test_progress_emitter()
    
    print("=" * 50)
    if imports_ok and emitter_ok:
        print("✓ All tests passed! Socket.IO implementation looks good.")
        return 0
    else:
        print("✗ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
