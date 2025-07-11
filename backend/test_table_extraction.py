#!/usr/bin/env python3
"""
Test script for table extraction functionality.
"""

import asyncio
import sys
from pathlib import Path
import logging

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.table_extraction_service import get_table_extraction_service
from app.parsers.parser_factory import ParserFactory
from app.parsers.markdown_generator import MarkdownGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_table_extraction_service():
    """Test the table extraction service directly."""
    print("Testing table extraction service...")
    
    try:
        service = await get_table_extraction_service()
        print(f"✓ Table extraction service initialized successfully")
        
        # Test with a sample PDF (if available)
        sample_pdf = Path("uploads").glob("*.pdf")
        sample_pdf = next(sample_pdf, None)
        
        if sample_pdf:
            print(f"Testing with PDF: {sample_pdf}")
            tables = await service.extract_tables_from_pdf(sample_pdf)
            print(f"✓ Extracted {len(tables)} tables from PDF")
            
            # Display first table if available
            if tables:
                first_table = tables[0]
                print(f"First table:")
                print(f"  Headers: {first_table.headers}")
                print(f"  Rows: {len(first_table.rows)}")
                print(f"  Method: {first_table.style.get('extraction_method', 'unknown')}")
                
                # Test markdown formatting
                markdown = service.format_table_to_markdown(first_table)
                print(f"  Markdown preview (first 300 chars):")
                print(f"  {markdown[:300]}...")
                
        else:
            print("⚠ No sample PDF found in uploads directory")
            
    except Exception as e:
        print(f"✗ Error testing table extraction service: {e}")
        import traceback
        traceback.print_exc()


async def test_pdf_parser_with_tables():
    """Test the PDF parser with enhanced table extraction."""
    print("\nTesting PDF parser with table extraction...")
    
    try:
        # Find a sample PDF
        sample_pdf = Path("uploads").glob("*.pdf")
        sample_pdf = next(sample_pdf, None)
        
        if not sample_pdf:
            print("⚠ No sample PDF found in uploads directory")
            return
            
        print(f"Testing with PDF: {sample_pdf}")
        
        # Create parser
        factory = ParserFactory()
        parser = factory.get_parser(sample_pdf)
        
        # Parse document
        ast = await parser.parse(sample_pdf)
        
        print(f"✓ Parsed document successfully")
        print(f"  Text blocks: {len(ast.textBlocks)}")
        print(f"  Images: {len(ast.images)}")
        print(f"  Tables: {len(ast.tables)}")
        print(f"  Math blocks: {len(ast.math)}")
        
        # Test markdown generation
        if ast.tables:
            markdown_gen = MarkdownGenerator()
            markdown = markdown_gen.generate(ast)
            
            print(f"✓ Generated markdown successfully")
            print(f"  Length: {len(markdown)} characters")
            
            # Save sample output
            output_path = Path("test_table_extraction_output.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"✓ Sample output saved to {output_path}")
            
        else:
            print("⚠ No tables found in document")
            
    except Exception as e:
        print(f"✗ Error testing PDF parser: {e}")
        import traceback
        traceback.print_exc()


async def test_image_parser_with_tables():
    """Test the image parser with table extraction."""
    print("\nTesting image parser with table extraction...")
    
    try:
        # Find a sample image
        sample_image = None
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            sample_image = next(Path("uploads").glob(f"*{ext}"), None)
            if sample_image:
                break
        
        if not sample_image:
            print("⚠ No sample image found in uploads directory")
            return
            
        print(f"Testing with image: {sample_image}")
        
        # Create parser
        factory = ParserFactory()
        parser = factory.get_parser(sample_image)
        
        # Parse document
        ast = await parser.parse(sample_image)
        
        print(f"✓ Parsed image successfully")
        print(f"  Images: {len(ast.images)}")
        print(f"  Tables: {len(ast.tables)}")
        
        if ast.tables:
            print(f"✓ Found {len(ast.tables)} tables in image")
            
            # Test markdown generation
            markdown_gen = MarkdownGenerator()
            markdown = markdown_gen.generate(ast)
            
            print(f"✓ Generated markdown successfully")
            print(f"  Length: {len(markdown)} characters")
            
        else:
            print("⚠ No tables found in image")
            
    except Exception as e:
        print(f"✗ Error testing image parser: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Table Extraction Test Suite")
    print("=" * 60)
    
    await test_table_extraction_service()
    await test_pdf_parser_with_tables()
    await test_image_parser_with_tables()
    
    print("\n" + "=" * 60)
    print("Test suite completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 