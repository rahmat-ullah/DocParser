# Markdown Download and Export API Documentation

## Overview

This document describes the API endpoints for downloading and exporting documents in various formats, with a focus on Markdown files.

## Endpoints

### 1. Download Markdown File

Downloads the saved Markdown file for a processed document.

**Endpoint:** `GET /api/v1/documents/{document_id}/markdown`

**Parameters:**
- `document_id` (path parameter): The unique identifier of the document

**Response:**
- **200 OK**: Returns the Markdown file as an attachment
  - Content-Type: `text/markdown`
  - Content-Disposition: `attachment; filename="{original_filename}.md"`
- **404 Not Found**: Document not found
- **409 Conflict**: 
  - Document processing not completed
  - Markdown file not generated
  - Markdown file path exists in database but file not found on disk

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/documents/123e4567-e89b-12d3-a456-426614174000/markdown" \
  -H "Accept: text/markdown" \
  --output document.md
```

**Example Response Headers:**
```
HTTP/1.1 200 OK
Content-Type: text/markdown
Content-Disposition: attachment; filename="example_document.md"
Content-Length: 1234
```

### 2. Export Document

Export a document in various formats with options.

**Endpoint:** `POST /api/v1/export/{document_id}`

**Parameters:**
- `document_id` (path parameter): The unique identifier of the document

**Request Body:**
```json
{
  "format": "markdown",
  "options": {
    "cached": true,
    "include_metadata": true
  }
}
```

**Fields:**
- `format` (string, required): Export format (markdown, pdf, docx, html)
- `options` (object, optional):
  - `cached` (boolean): Use cached file if available (default: false)
  - `include_metadata` (boolean): Include document metadata (default: true)

**Response:**
- **200 OK**: Returns the exported file
- **404 Not Found**: Document not found
- **409 Conflict**: Document processing not completed
- **400 Bad Request**: Invalid format or export options
- **501 Not Implemented**: Export format not yet supported

**Special Behavior:**
When `format="markdown"` and `options.cached=true`, this endpoint reuses the same logic as the `/documents/{id}/markdown` endpoint.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/export/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "markdown",
    "options": {
      "cached": true
    }
  }' \
  --output exported.md
```

### 3. Get Available Export Formats

Get the list of available export formats for a document.

**Endpoint:** `GET /api/v1/export/{document_id}/formats`

**Parameters:**
- `document_id` (path parameter): The unique identifier of the document

**Response:**
- **200 OK**: Returns available export formats
- **404 Not Found**: Document not found

**Example Response:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "processing_status": "completed",
  "available_formats": [
    {
      "format": "markdown",
      "cached": true,
      "description": "Cached markdown file"
    },
    {
      "format": "markdown",
      "cached": false,
      "description": "Generate markdown on-the-fly"
    },
    {
      "format": "pdf",
      "cached": false,
      "description": "Export as PDF (not yet implemented)"
    },
    {
      "format": "docx",
      "cached": false,
      "description": "Export as Word document (not yet implemented)"
    },
    {
      "format": "html",
      "cached": false,
      "description": "Export as HTML (not yet implemented)"
    }
  ]
}
```

## Integration Notes

1. The markdown download endpoint checks for:
   - Document existence
   - Processing completion status
   - Presence of `markdown_path` in the database
   - Actual file existence on disk

2. The export endpoint provides a unified interface for all export formats and intelligently reuses the markdown download logic when appropriate.

3. The formats endpoint helps clients discover what export options are available for a given document.

## Error Handling

All endpoints follow consistent error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error scenarios:
- **404**: Document ID doesn't exist in the database
- **409**: Document exists but isn't ready for export (processing incomplete or file missing)
- **400**: Invalid request parameters or unsupported format
- **501**: Requested feature not yet implemented
