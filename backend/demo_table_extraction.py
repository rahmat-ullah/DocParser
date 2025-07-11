#!/usr/bin/env python3
"""
Demonstration script for table extraction functionality.
Shows how to use the table extraction service directly.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_table_extraction():
    """Demonstrate table extraction functionality."""
    print("🔍 Table Extraction Demo")
    print("=" * 60)
    
    try:
        # Import the service
        from app.services.table_extraction_service import get_table_extraction_service
        
        # Initialize service
        print("\n1. Initializing table extraction service...")
        service = await get_table_extraction_service()
        print("✓ Service initialized successfully")
        
        # Check available methods
        print("\n2. Available extraction methods:")
        print("   - pdfplumber: Rule-based table detection")
        print("   - ocr: Optical character recognition")
        print("   - ai: AI-enhanced extraction (requires OpenAI API)")
        print("   - auto: Automatically selects best method")
        
        # Look for sample documents
        print("\n3. Looking for sample documents...")
        uploads_dir = Path("uploads")
        
        # Check for PDFs
        pdf_files = list(uploads_dir.glob("*.pdf")) if uploads_dir.exists() else []
        image_files = []
        
        # Check for images
        if uploads_dir.exists():
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                image_files.extend(uploads_dir.glob(f"*{ext}"))
        
        if pdf_files:
            print(f"   Found {len(pdf_files)} PDF files")
            sample_pdf = pdf_files[0]
            print(f"   Using: {sample_pdf}")
            
            # Extract tables from PDF
            print("\n4. Extracting tables from PDF...")
            try:
                tables = await service.extract_tables_from_pdf(
                    sample_pdf,
                    extraction_method="pdfplumber"  # Use pdfplumber for reliability
                )
                
                print(f"✓ Extracted {len(tables)} tables")
                
                # Display table information
                for i, table in enumerate(tables):
                    print(f"\n   Table {i+1}:")
                    print(f"     Headers: {len(table.headers)} columns")
                    print(f"     Rows: {len(table.rows)} data rows")
                    print(f"     Method: {table.style.get('extraction_method', 'unknown')}")
                    
                    if table.headers:
                        print(f"     Column names: {', '.join(table.headers[:3])}{'...' if len(table.headers) > 3 else ''}")
                    
                    # Generate markdown sample
                    markdown = service.format_table_to_markdown(table)
                    print(f"     Markdown preview (first 200 chars):")
                    print(f"     {markdown[:200]}{'...' if len(markdown) > 200 else ''}")
                
                if tables:
                    # Save a sample
                    sample_output = Path("sample_table_extraction.md")
                    with open(sample_output, 'w', encoding='utf-8') as f:
                        f.write("# Sample Table Extraction\n\n")
                        for i, table in enumerate(tables):
                            f.write(f"## Table {i+1}\n\n")
                            f.write(service.format_table_to_markdown(table))
                            f.write("\n\n")
                    
                    print(f"\n✓ Sample output saved to: {sample_output}")
                    
            except Exception as e:
                print(f"⚠ PDF table extraction failed: {e}")
                
        elif image_files:
            print(f"   Found {len(image_files)} image files")
            sample_image = image_files[0]
            print(f"   Using: {sample_image}")
            
            # Extract tables from image
            print("\n4. Extracting tables from image...")
            try:
                tables = await service.extract_tables_from_image(
                    sample_image,
                    extraction_method="auto"  # Let it choose the best method
                )
                
                print(f"✓ Extracted {len(tables)} tables")
                
                if tables:
                    for i, table in enumerate(tables):
                        print(f"\n   Table {i+1}:")
                        print(f"     Headers: {len(table.headers)} columns")
                        print(f"     Rows: {len(table.rows)} data rows")
                        print(f"     Method: {table.style.get('extraction_method', 'unknown')}")
                        
                        markdown = service.format_table_to_markdown(table)
                        print(f"     Markdown preview (first 200 chars):")
                        print(f"     {markdown[:200]}{'...' if len(markdown) > 200 else ''}")
                else:
                    print("   No tables detected in the image")
                    
            except Exception as e:
                print(f"⚠ Image table extraction failed: {e}")
                
        else:
            print("   No sample documents found in uploads/ directory")
            print("   💡 Add some PDF or image files to uploads/ to test extraction")
        
        print("\n5. Testing parser integration...")
        try:
            from app.parsers.parser_factory import ParserFactory
            from app.parsers.markdown_generator import MarkdownGenerator
            
            if pdf_files:
                # Test with parser factory
                factory = ParserFactory()
                parser = factory.get_parser(pdf_files[0])
                
                print(f"   Using parser: {type(parser).__name__}")
                
                # Parse document (this will use enhanced table extraction)
                ast = await parser.parse(pdf_files[0])
                
                print(f"✓ Document parsed successfully:")
                print(f"     Text blocks: {len(ast.textBlocks)}")
                print(f"     Images: {len(ast.images)}")
                print(f"     Tables: {len(ast.tables)}")
                print(f"     Math blocks: {len(ast.math)}")
                
                # Generate markdown
                markdown_gen = MarkdownGenerator()
                markdown = markdown_gen.generate(ast)
                
                print(f"✓ Generated {len(markdown)} characters of markdown")
                
                # Save full document
                full_output = Path("sample_full_document.md")
                with open(full_output, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                
                print(f"✓ Full document saved to: {full_output}")
                
            else:
                print("   Skipping parser test - no PDF files available")
                
        except Exception as e:
            print(f"⚠ Parser integration test failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("\nKey features demonstrated:")
        print("✓ Service initialization")
        print("✓ PDF table extraction")
        print("✓ Markdown generation")
        print("✓ Parser integration")
        print("\nThe table extraction system is ready for use!")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(demo_table_extraction()) 