# Step 5: Expose markdown_url in Status and Result Endpoints

## Overview
This implementation adds a `markdown_url` field to the existing status and result endpoints, making it easy for the UI to link to or download the generated markdown files.

## Changes Made

### 1. Modified Endpoints

#### GET /{document_id}/status
- **File**: `app/api/v1/endpoints/processing.py`
- **Function**: `get_processing_status`
- **Changes**:
  - Added `Request` parameter to the endpoint
  - Added `markdown_url` field to the response using `request.url_for("download_markdown", document_id=document_id)`
  - The URL is included regardless of document processing status

#### GET /{document_id}/result
- **File**: `app/api/v1/endpoints/processing.py`
- **Function**: `get_processing_result`
- **Changes**:
  - Added `Request` parameter to the endpoint
  - Added `markdown_url` field to the response using `request.url_for("download_markdown", document_id=document_id)`

### 2. Response Format Examples

#### Status Endpoint Response
```json
{
  "document_id": "test-123",
  "status": "completed",
  "started_at": "2024-01-10T10:00:00",
  "completed_at": "2024-01-10T10:05:00",
  "error": null,
  "result": "# Document Content...",
  "markdown_url": "http://localhost:8000/api/v1/documents/test-123/markdown"
}
```

#### Result Endpoint Response
```json
{
  "document_id": "test-123",
  "extracted_text": "# Document Content...",
  "ai_description": "AI-generated description",
  "completed_at": "2024-01-10T10:05:00",
  "markdown_url": "http://localhost:8000/api/v1/documents/test-123/markdown"
}
```

## Implementation Details

### URL Generation
- Uses FastAPI's `request.url_for()` method to generate absolute URLs
- The URL points to the existing `download_markdown` endpoint in the documents router
- The generated URL includes the full base URL (protocol, host, port) making it suitable for direct use by UI clients

### Benefits
1. **Consistent URLs**: URLs are generated dynamically based on the current server configuration
2. **No hardcoding**: The URL generation uses FastAPI's routing system, ensuring consistency
3. **Ready for UI**: The absolute URL can be used directly in download links or iframe src attributes

## Testing
A comprehensive test suite was created in `tests/test_markdown_url.py` that verifies:
1. The `markdown_url` field is present in status endpoint responses
2. The `markdown_url` field is present in result endpoint responses
3. The URL format is correct and points to the download endpoint
4. The URL is included even for documents still being processed

## Usage Example
```python
# Get document status with markdown URL
response = requests.get("http://localhost:8000/api/v1/processing/doc-123/status")
data = response.json()
markdown_url = data["markdown_url"]

# Download the markdown file
markdown_response = requests.get(markdown_url)
markdown_content = markdown_response.text
```

## Notes
- The `markdown_url` is always included in the response, even if the document processing is not complete
- Attempting to download from the URL when processing is incomplete will return a 409 error
- The URL uses the same authentication and authorization as other API endpoints
