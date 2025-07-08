#!/usr/bin/env python3
"""
Test script for the document processing pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_processor import DocumentProcessor


async def test_txt_processing():
    """Test processing a simple text file."""
    processor = DocumentProcessor()
    
    # Create a test text file
    test_file = Path("test_document.txt")
    test_file.write_text("""
# Test Document

This is a **test document** for the parsing pipeline.

## Features
- Text extraction
- Heading detection
- List processing

### Code Example
```python
def hello_world():
    print("Hello, World!")
```

> This is a quote block.

The end.
""")
    
    try:
        print("Testing document processing pipeline...")
        print("=" * 50)
        
        async for progress in processor.process_document(test_file, enable_ai_processing=False):
            print(f"[{progress.stage}] {progress.progress:.0%} - {progress.message}")
            if progress.details:
                print(f"  Details: {progress.details}")
            
            # Print final result
            if progress.result:
                print("\nFinal Markdown Output:")
                print("-" * 30)
                print(progress.result)
                print("-" * 30)
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


async def test_supported_formats():
    """Test getting supported formats."""
    processor = DocumentProcessor()
    formats = processor.get_supported_formats()
    
    print("\nSupported formats:")
    print("=" * 20)
    print(f"Extensions: {formats['supported_extensions']}")
    print(f"Capabilities: {formats['capabilities']}")


async def main():
    """Run all tests."""
    await test_supported_formats()
    await test_txt_processing()


if __name__ == "__main__":
    asyncio.run(main())
