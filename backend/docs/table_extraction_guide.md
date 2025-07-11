# Table Extraction Guide

## Overview

The DocParser application now includes comprehensive table extraction capabilities that can detect and extract tables from various document types including PDFs and images. The system supports multiple extraction methods and can output tables in properly formatted markdown.

## Features

### Multiple Extraction Methods

1. **Rule-based extraction (pdfplumber)**: Uses pdfplumber's sophisticated table detection algorithms to identify tables based on document structure and text positioning.

2. **OCR-based extraction (EasyOCR)**: Uses optical character recognition to extract tables from images or scanned documents where text-based extraction fails.

3. **AI-enhanced extraction (OpenAI Vision API)**: Leverages OpenAI's Vision API to intelligently identify and extract table structures from complex documents.

4. **Automatic method selection**: Intelligently chooses the best extraction method based on document type and content.

### Supported Document Types

- **PDF documents**: Full support for text-based PDFs with advanced table detection
- **Image files**: JPG, PNG, GIF, BMP, TIFF, WebP images containing tables
- **Scanned documents**: OCR-based extraction for scanned PDFs and images

### Output Formats

- **Markdown tables**: Clean, properly formatted markdown tables
- **Structured data**: TableBlock objects with headers, rows, and metadata
- **Extraction metadata**: Information about confidence scores and extraction methods

## Installation

### Required Dependencies

The table extraction functionality requires additional Python packages:

```bash
pip install pdfplumber==0.11.7
pip install opencv-python==4.10.0.84
pip install easyocr==1.7.1
```

These dependencies are automatically included when you install the application requirements:

```bash
pip install -r requirements.txt
```

**Note**: EasyOCR is optional. If it fails to install or initialize (common on some systems due to PyTorch compatibility issues), the system will automatically disable OCR-based extraction while keeping pdfplumber and AI-based extraction methods working.

## Usage

### Basic Usage

The table extraction functionality is automatically integrated into the document parsing pipeline. When you upload a document, tables will be automatically detected and extracted.

### API Usage

#### Direct Service Usage

```python
from app.services.table_extraction_service import get_table_extraction_service
from pathlib import Path

# Initialize the service
service = await get_table_extraction_service()

# Extract tables from a PDF
tables = await service.extract_tables_from_pdf(
    Path("document.pdf"),
    extraction_method="auto"  # or "pdfplumber", "ocr", "ai"
)

# Extract tables from an image
tables = await service.extract_tables_from_image(
    Path("table_image.png"),
    extraction_method="auto"
)

# Format table to markdown
for table in tables:
    markdown = service.format_table_to_markdown(table)
    print(markdown)
```

#### Using Parsers

```python
from app.parsers.parser_factory import ParserFactory
from app.parsers.markdown_generator import MarkdownGenerator

# Create parser
factory = ParserFactory()
parser = factory.get_parser(Path("document.pdf"))

# Parse document (tables will be automatically extracted)
ast = await parser.parse(Path("document.pdf"))

# Generate markdown with tables
markdown_gen = MarkdownGenerator()
markdown = markdown_gen.generate(ast)
```

### Configuration Options

#### Table Extraction Settings

You can customize table extraction behavior by passing settings:

```python
table_settings = {
    "vertical_strategy": "lines",      # "lines", "lines_strict", "text", "explicit"
    "horizontal_strategy": "lines",    # "lines", "lines_strict", "text", "explicit"
    "snap_tolerance": 3,               # Line snapping tolerance
    "join_tolerance": 3,               # Line joining tolerance
    "edge_min_length": 3,              # Minimum edge length
    "min_words_vertical": 3,           # Minimum words for vertical alignment
    "min_words_horizontal": 1,         # Minimum words for horizontal alignment
    "intersection_tolerance": 3,       # Intersection detection tolerance
    "text_tolerance": 3,               # Text alignment tolerance
}

tables = await service.extract_tables_from_pdf(
    pdf_path,
    extraction_method="pdfplumber",
    table_settings=table_settings
)
```

#### Extraction Methods

- **`"auto"`**: Automatically selects the best method (default)
- **`"pdfplumber"`**: Uses pdfplumber for rule-based extraction
- **`"ocr"`**: Uses OCR for optical character recognition
- **`"ai"`**: Uses OpenAI Vision API for AI-enhanced extraction

## Architecture

### TableExtractionService

The core service that handles all table extraction operations:

```python
class TableExtractionService:
    async def extract_tables_from_pdf(self, pdf_path, extraction_method="auto", table_settings=None)
    async def extract_tables_from_image(self, image_path, extraction_method="auto")
    def format_table_to_markdown(self, table)
    # ... other methods
```

### TableBlock Model

Represents extracted table data:

```python
class TableBlock(BaseModel):
    headers: List[str]              # Column headers
    rows: List[List[str]]          # Table rows
    bbox: Optional[Dict[str, float]]  # Bounding box coordinates
    caption: Optional[str]         # Table caption
    style: Dict[str, Any]          # Extraction metadata
```

### Integration Points

1. **PDF Parser**: Enhanced with advanced table extraction
2. **Image Parser**: Now extracts tables from images
3. **Markdown Generator**: Improved table formatting with metadata
4. **AST Models**: TableBlock includes extraction metadata

## Examples

### Simple Table Extraction

```python
# Extract tables from a PDF
service = await get_table_extraction_service()
tables = await service.extract_tables_from_pdf(Path("report.pdf"))

print(f"Found {len(tables)} tables")
for i, table in enumerate(tables):
    print(f"\nTable {i+1}:")
    print(f"Headers: {table.headers}")
    print(f"Rows: {len(table.rows)}")
    print(f"Method: {table.style.get('extraction_method')}")
```

### Custom Table Settings

```python
# Use custom settings for better accuracy
settings = {
    "vertical_strategy": "text",
    "horizontal_strategy": "lines",
    "min_words_vertical": 5,
    "text_tolerance": 5,
}

tables = await service.extract_tables_from_pdf(
    Path("complex_document.pdf"),
    extraction_method="pdfplumber",
    table_settings=settings
)
```

### OCR-based Extraction

```python
# Force OCR extraction for scanned documents
tables = await service.extract_tables_from_pdf(
    Path("scanned_document.pdf"),
    extraction_method="ocr"
)
```

### AI-enhanced Extraction

```python
# Use AI for complex table structures
tables = await service.extract_tables_from_pdf(
    Path("complex_table.pdf"),
    extraction_method="ai"
)
```

## Output Format

### Markdown Tables

Tables are formatted as standard markdown tables:

```markdown
**Table 1 from page 1**

| Name | Age | City |
| --- | --- | --- |
| John | 25 | New York |
| Jane | 30 | Los Angeles |
| Bob | 35 | Chicago |

<!-- Table extracted using pdfplumber (confidence: 0.95) -->
```

### Structured Data

Tables are represented as `TableBlock` objects:

```python
TableBlock(
    headers=["Name", "Age", "City"],
    rows=[
        ["John", "25", "New York"],
        ["Jane", "30", "Los Angeles"],
        ["Bob", "35", "Chicago"]
    ],
    bbox={"x0": 100, "y0": 200, "x1": 400, "y1": 350, "page": 0},
    caption="Table 1 from page 1",
    style={
        "extraction_method": "pdfplumber",
        "confidence": 0.95
    }
)
```

## Testing

### Running Tests

A comprehensive test suite is available:

```bash
cd backend
python test_table_extraction.py
```

### Test Coverage

The test suite covers:
- Service initialization
- PDF table extraction
- Image table extraction
- Markdown generation
- Error handling
- Integration with parsers

### Manual Testing

1. Place test documents in the `uploads/` directory
2. Run the test script
3. Check generated markdown output
4. Verify table extraction accuracy

## Troubleshooting

### Common Issues

1. **No tables detected**: 
   - Try different extraction methods
   - Adjust table settings
   - Verify document quality

2. **OCR initialization failure**:
   - EasyOCR has known compatibility issues with some PyTorch versions
   - The system will automatically disable OCR if it fails to initialize
   - OCR functionality is optional - pdfplumber and AI methods will still work
   - To fix OCR issues, try:
     ```bash
     pip uninstall torch torchvision easyocr
     pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
     pip install easyocr
     ```

3. **AI extraction not working**:
   - Check OpenAI API key configuration
   - Verify API quotas and limits
   - Ensure proper network connectivity

4. **Poor table quality**:
   - Adjust extraction tolerances
   - Try different extraction strategies
   - Consider preprocessing the document

### Performance Considerations

- **pdfplumber**: Fast, works well with text-based PDFs
- **OCR**: Slower, but works with scanned documents
- **AI**: Slower and requires API calls, but most accurate for complex tables
- **auto**: Balances speed and accuracy

### Memory Usage

- OCR models require significant memory (~500MB+)
- Large documents may require increased memory limits
- Consider batch processing for many documents

## API Reference

### TableExtractionService

#### Methods

##### `extract_tables_from_pdf(pdf_path, extraction_method="auto", table_settings=None)`

Extract tables from a PDF file.

**Parameters:**
- `pdf_path` (Path): Path to the PDF file
- `extraction_method` (str): Extraction method ("auto", "pdfplumber", "ocr", "ai")
- `table_settings` (dict): Custom table extraction settings

**Returns:** List[TableBlock]

##### `extract_tables_from_image(image_path, extraction_method="auto")`

Extract tables from an image file.

**Parameters:**
- `image_path` (Path): Path to the image file
- `extraction_method` (str): Extraction method ("auto", "ocr", "ai")

**Returns:** List[TableBlock]

##### `format_table_to_markdown(table)`

Format a table to markdown.

**Parameters:**
- `table` (TableBlock): Table to format

**Returns:** str (markdown formatted table)

## Future Enhancements

### Planned Features

1. **Advanced table recognition**: Better detection of complex table structures
2. **Table merging**: Combine tables that span multiple pages
3. **Cell formatting**: Preserve cell formatting and styles
4. **Table validation**: Quality checks and error detection
5. **Batch processing**: Process multiple documents efficiently
6. **Custom output formats**: Export to CSV, Excel, JSON

### Contributing

To contribute to the table extraction functionality:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

### License

This table extraction functionality is part of the DocParser application and follows the same license terms. 