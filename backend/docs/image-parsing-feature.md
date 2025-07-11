# Image and Diagram Context Parsing Feature

## Overview

The Document Parser backend includes advanced image and diagram context parsing capabilities powered by OpenAI's GPT-4o Vision model. This feature automatically extracts meaningful context from visual elements within documents, making them searchable and accessible in the generated Markdown output.

## How It Works

### 1. Image Detection
During document processing, the system automatically detects and extracts images from:
- PDF documents
- Word documents (DOCX)
- PowerPoint presentations (PPTX)
- Other supported formats

### 2. Context Extraction
For each detected image, the system:
1. Converts the image to base64 format
2. Sends it to OpenAI's GPT-4o Vision API
3. Receives a detailed description of the visual content
4. Falls back to OCR if Vision API fails

### 3. Integration
The extracted context is seamlessly integrated into the Markdown output with:
- Original image reference
- AI-generated description
- Preserved formatting and structure

## Configuration

### Required Settings
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_VISION_MODEL=gpt-4o  # GPT-4o model for best results
```

### Optional Settings
```env
# OCR Fallback
OCR_FALLBACK_ENABLED=true  # Enable OCR fallback (default: true)
TESSERACT_PATH=           # Path to Tesseract executable (optional)

# Performance Tuning
OPENAI_MAX_RETRIES=3      # Number of retry attempts
OPENAI_RETRY_DELAY=1.0    # Initial retry delay in seconds
OPENAI_TIMEOUT=30         # Request timeout in seconds
```

## Features

### Supported Visual Elements
- **Text in Images**: Extracts text from screenshots, scanned documents, and images
- **Tables**: Identifies and describes table structures and content
- **Charts & Graphs**: Analyzes data visualizations including:
  - Bar charts
  - Line graphs
  - Pie charts
  - Flow diagrams
- **Diagrams**: Understands and describes:
  - System architectures
  - Flowcharts
  - UML diagrams
  - Network diagrams
- **Infographics**: Extracts key information from complex visual presentations

### Output Format
The feature generates structured descriptions that include:
- Main visual elements and their relationships
- Text content within images
- Data points from charts and graphs
- Spatial relationships between elements
- Colors and visual hierarchy (when relevant)

## Example Outputs

### Example 1: System Architecture Diagram
```markdown
![System Architecture](architecture.png)

AI Description: This diagram illustrates a microservices architecture with the following components:

1. **Frontend Layer**: React-based web application with responsive design
2. **API Gateway**: Central entry point handling authentication and routing
3. **Microservices**:
   - User Service: Handles user authentication and profiles
   - Document Service: Manages document storage and retrieval
   - Processing Service: Performs AI-powered document analysis
4. **Data Layer**: 
   - PostgreSQL for relational data
   - Redis for caching
   - S3 for document storage

The services communicate via REST APIs with JWT authentication. All services are containerized using Docker and orchestrated with Kubernetes.
```

### Example 2: Data Visualization
```markdown
![Sales Chart](sales_q4_2023.png)

AI Description: This bar chart displays quarterly sales data for Q4 2023:

- October: $2.3M (15% increase from previous month)
- November: $2.8M (22% increase, highest in quarter)
- December: $2.5M (11% decrease due to seasonal factors)

The chart uses blue bars with values displayed above each bar. A trend line shows overall growth of 18% for the quarter. The y-axis shows revenue in millions USD, while the x-axis displays months.
```

### Example 3: Flowchart
```markdown
![Process Flow](document_processing_flow.png)

AI Description: This flowchart depicts the document processing workflow:

1. START: User uploads document
2. Validation: Check file type and size
   - If invalid → Display error → END
   - If valid → Continue
3. Extract Content: Parse document structure
4. Process Images: Extract and analyze visual elements
5. Generate Markdown: Convert to structured format
6. Save Results: Store in database
7. Notify User: Send completion notification
8. END: Process complete

Decision points are shown as diamonds, processes as rectangles, and flow direction with arrows.
```

## Error Handling

### Vision API Failures
When the Vision API fails, the system:
1. Logs the error with details
2. Attempts retry with exponential backoff
3. Falls back to OCR if enabled
4. Provides descriptive error message in output

### OCR Fallback
If Vision API is unavailable:
```markdown
![Image](image.png)

OCR Extracted Text: [Text extracted via Tesseract OCR]
```

### Complete Failure
If both Vision API and OCR fail:
```markdown
![Image](image.png)

(AI description failed: Both Vision API and OCR failed. Vision API: [error], OCR: [error])
```

## Performance Considerations

### API Rate Limits
- GPT-4o has rate limits that vary by account tier
- The system implements retry logic with exponential backoff
- Consider implementing request queuing for high-volume processing

### Image Optimization
- Large images are automatically resized to optimize API calls
- Maximum image size: 20MB (OpenAI limit)
- Supported formats: PNG, JPEG, GIF, WebP

### Cost Management
- Each image analysis consumes tokens based on image size
- Monitor usage through OpenAI dashboard
- Consider implementing usage limits per user/document

## Best Practices

### For Optimal Results
1. **Image Quality**: Higher resolution images yield better descriptions
2. **Clear Visuals**: Well-structured diagrams and charts are more accurately described
3. **Text in Images**: Ensure text is legible (minimum 12pt equivalent)
4. **File Formats**: Use PNG or high-quality JPEG for best results

### Security Considerations
1. **API Keys**: Store securely in environment variables
2. **Image Content**: Be aware that images are sent to OpenAI for processing
3. **Sensitive Data**: Consider redacting sensitive information before processing
4. **Data Retention**: OpenAI doesn't retain images sent via API

## Troubleshooting

### Common Issues

#### "Unsupported parameter: 'max_tokens'"
**Cause**: Older OpenAI library version
**Solution**: Update OpenAI library or use compatible parameters

#### "Vision API failed after X attempts"
**Cause**: API rate limit or network issues
**Solution**: 
- Check API key validity
- Verify network connectivity
- Wait and retry later

#### "OCR extraction failed: tesseract is not installed"
**Cause**: Tesseract not installed on system
**Solution**: 
- Install Tesseract: https://github.com/tesseract-ocr/tesseract
- Set TESSERACT_PATH in environment variables

## Future Enhancements

### Planned Features
- Support for video frame extraction and analysis
- Multi-language OCR support
- Custom prompt templates for specific diagram types
- Local vision model integration for privacy-sensitive documents
- Batch processing optimization
- Caching of processed images

### Integration Possibilities
- Elasticsearch integration for visual content search
- Automatic diagram recreation using Mermaid/PlantUML
- Visual similarity search across documents
- Real-time collaborative annotation

## API Reference

### Processing Endpoint
```
POST /api/v1/processing/{document_id}
```

Request body:
```json
{
  "processing_options": {
    "use_ai": true,
    "extract_images": true,
    "vision_model": "gpt-4o",
    "include_ocr_fallback": true
  }
}
```

### Image Metadata Endpoints

#### Get All Images in Document
```
GET /api/v1/images/documents/{document_id}/images
```

Response:
```json
{
  "images": [
    {
      "id": "fig-001",
      "type": "diagram",
      "title": "System Architecture",
      "caption": "Shows the system components",
      "source": {
        "filename": "document.pdf",
        "page": 5,
        "documentSection": "Chapter 3"
      },
      "description": "...",
      "linkedEntities": [...],
      "semanticTags": [...],
      "aiAnnotations": {...}
    }
  ],
  "documentId": "doc-123",
  "totalImages": 5
}
```

#### Get Specific Image Metadata
```
GET /api/v1/images/documents/{document_id}/images/{image_id}
```

Response: Single ImageMetadata object

#### Trigger Image Analysis
```
POST /api/v1/images/documents/{document_id}/analyze-images?force_reanalysis=false
```

Response:
```json
{
  "message": "Image analysis queued",
  "document_id": "doc-123",
  "status": "pending"
}
```

### Configuration via Environment
All image processing behavior can be configured through environment variables without code changes.

## Conclusion

The image and diagram context parsing feature transforms visual content into searchable, accessible text, making documents truly comprehensible for both humans and machines. By leveraging GPT-4o's advanced vision capabilities, the system provides accurate, detailed descriptions that preserve the meaning and context of visual elements.
