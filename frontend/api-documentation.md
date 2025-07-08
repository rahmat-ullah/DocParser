# Document Parser Web Application - API Documentation

## Overview

This API documentation covers all endpoints for the Document Parser Web Application. The API provides comprehensive document processing, search, export, and history management capabilities.

## Base URL
```
http://localhost:3000/api
```

## Authentication
Currently, the API operates without authentication for development purposes. In production, implement appropriate authentication mechanisms.

## Common Response Format

All API responses follow a consistent structure:

```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata: {
    timestamp: string;
    requestId: string;
    processingTime?: number;
  };
}
```

## File Upload and Processing

### Upload Document
**POST** `/api/upload`

Upload a file for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File to upload (required)
  - `options`: JSON string with processing options (optional)

**Supported File Types:**
- PDF: `.pdf`
- Microsoft Word: `.docx`
- Microsoft Excel: `.xlsx`
- Microsoft PowerPoint: `.pptx`
- Text: `.txt`
- Images: `.png`, `.jpg`, `.jpeg`

**Maximum File Size:** 50MB

**Example Request:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('options', JSON.stringify({
  extractImages: true,
  extractTables: true,
  extractMath: true,
  outputFormat: 'markdown'
}));

fetch('/api/upload', {
  method: 'POST',
  body: formData
});
```

**Response:**
```typescript
interface UploadDocumentResponse {
  documentId: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  uploadUrl?: string;
  processingStatus: 'queued' | 'processing' | 'completed' | 'failed';
  estimatedProcessingTime?: number;
}
```

### Get Upload Configuration
**GET** `/api/upload`

Get upload configuration including max file size and supported types.

**Response:**
```typescript
{
  success: true,
  data: {
    maxFileSize: number;
    supportedTypes: string[];
  }
}
```

## Document Processing

### Process Document
**POST** `/api/process`

Convert uploaded document to markdown format.

**Request Body:**
```typescript
interface ProcessDocumentRequest {
  documentId: string;
  options?: {
    extractImages?: boolean;
    extractTables?: boolean;
    extractMath?: boolean;
    preserveFormatting?: boolean;
    language?: string;
    ocrEngine?: 'tesseract' | 'google' | 'aws';
  };
}
```

**Response:**
```typescript
interface ParsedDocument {
  id: string;
  metadata: DocumentMetadata;
  originalContent: string;
  markdownContent: string;
  sections: DocumentSection[];
  images: ExtractedImage[];
  tables: ExtractedTable[];
  mathExpressions: MathExpression[];
}
```

**Example Request:**
```javascript
fetch('/api/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    documentId: 'doc-123',
    options: {
      extractImages: true,
      extractTables: true,
      language: 'en'
    }
  })
});
```

## Document Export

### Export Document
**POST** `/api/export`

Export processed document in various formats.

**Request Body:**
```typescript
interface ExportRequest {
  documentId: string;
  format: 'markdown' | 'json' | 'html' | 'txt';
  options?: {
    includeImages?: boolean;
    includeTables?: boolean;
    includeMath?: boolean;
    includeMetadata?: boolean;
  };
}
```

**Response:**
```typescript
interface ExportResponse {
  downloadUrl: string;
  fileName: string;
  fileSize: number;
  format: string;
  expiresAt: string;
}
```

**Example Request:**
```javascript
fetch('/api/export', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    documentId: 'doc-123',
    format: 'html',
    options: {
      includeImages: true,
      includeMetadata: true
    }
  })
});
```

### Get Export Formats
**GET** `/api/export`

Get list of available export formats.

**Response:**
```typescript
{
  success: true,
  data: {
    formats: string[];
  }
}
```

## Document History

### Get Document History
**GET** `/api/history`

Retrieve document processing history with filtering and pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `pageSize`: Items per page (default: 20, max: 100)
- `sortBy`: Sort field (`fileName`, `fileSize`, `uploadDate`, `lastAccessed`)
- `sortOrder`: Sort order (`asc` or `desc`)
- `fileType`: Filter by file types (comma-separated)
- `dateFrom`: Filter by upload date from (ISO string)
- `dateTo`: Filter by upload date to (ISO string)
- `tags`: Filter by tags (comma-separated)
- `hasImages`: Filter documents with images (true/false)
- `hasTables`: Filter documents with tables (true/false)
- `hasMath`: Filter documents with math (true/false)

**Example Request:**
```
GET /api/history?page=1&pageSize=10&sortBy=uploadDate&sortOrder=desc&fileType=pdf,docx&hasImages=true
```

**Response:**
```typescript
interface HistoryResponse {
  documents: DocumentHistoryEntry[];
  totalCount: number;
  page: number;
  pageSize: number;
}
```

### Add Document to History
**POST** `/api/history`

Add or update a document in history.

**Request Body:**
```typescript
interface DocumentHistoryEntry {
  id?: string;
  metadata: DocumentMetadata;
  markdownContent: string;
  jsonContent: ParsedDocument;
  tags?: string[];
  notes?: string;
}
```

### Delete from History
**DELETE** `/api/history`

Delete specific document or clear all history.

**Query Parameters:**
- `documentId`: Specific document ID to delete (optional)

**Examples:**
```javascript
// Delete specific document
fetch('/api/history?documentId=doc-123', { method: 'DELETE' });

// Clear all history
fetch('/api/history', { method: 'DELETE' });
```

## Search

### Search Documents
**POST** `/api/search`

Search within document content and metadata.

**Request Body:**
```typescript
interface SearchRequest {
  query: string;
  documentId?: string;
  searchIn?: ('content' | 'metadata')[];
  options?: {
    caseSensitive?: boolean;
    wholeWords?: boolean;
    regex?: boolean;
  };
}
```

**Response:**
```typescript
interface SearchResponse {
  results: SearchResult[];
  totalMatches: number;
  searchTime: number;
  query: string;
}

interface SearchResult {
  documentId: string;
  fileName: string;
  matches: Array<{
    type: 'content' | 'metadata';
    text: string;
    context: string;
    position?: {
      line: number;
      column: number;
    };
    confidence?: number;
  }>;
}
```

**Example Request:**
```javascript
fetch('/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'machine learning',
    searchIn: ['content', 'metadata'],
    options: {
      caseSensitive: false,
      wholeWords: true
    }
  })
});
```

### Get Search Suggestions
**GET** `/api/search`

Get search suggestions and recent searches.

**Query Parameters:**
- `prefix`: Search prefix for suggestions (optional)

**Response:**
```typescript
{
  success: true,
  data: {
    suggestions: string[];
    recentSearches: string[];
  }
}
```

## Health Check

### Get System Health
**GET** `/api/health`

Get application health status and metrics.

**Response:**
```typescript
interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  version: string;
  services: {
    database: ServiceHealth;
    storage: ServiceHealth;
    ai: ServiceHealth;
    processing: ServiceHealth;
  };
  metrics: {
    memoryUsage: NodeJS.MemoryUsage;
    requestCount: number;
    averageResponseTime: number;
    errorRate: number;
  };
  system: {
    nodeVersion: string;
    platform: string;
    arch: string;
    cpuUsage: number;
  };
}
```

### Reset Health Metrics
**POST** `/api/health`

Reset health monitoring metrics (admin only).

**Request Body:**
```typescript
{
  action: 'reset-metrics'
}
```

## Error Codes

Common error codes used across all endpoints:

| Code | Description |
|------|-------------|
| `MISSING_PARAMETERS` | Required parameters not provided |
| `INVALID_FILE_TYPE` | Unsupported file type |
| `FILE_TOO_LARGE` | File exceeds maximum size limit |
| `PROCESSING_ERROR` | Error during document processing |
| `DOCUMENT_NOT_FOUND` | Requested document not found |
| `EXPORT_ERROR` | Error during document export |
| `SEARCH_ERROR` | Error during search operation |
| `HISTORY_ERROR` | Error accessing document history |
| `VALIDATION_ERROR` | Input validation failed |
| `SERVER_ERROR` | Internal server error |

## Rate Limiting

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Premium users: 5000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per hour
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time (Unix timestamp)

## Usage Examples

### Complete Document Processing Workflow

```javascript
// 1. Upload document
const uploadFormData = new FormData();
uploadFormData.append('file', file);
const uploadResponse = await fetch('/api/upload', {
  method: 'POST',
  body: uploadFormData
});
const { data: uploadData } = await uploadResponse.json();

// 2. Process document
const processResponse = await fetch('/api/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    documentId: uploadData.documentId,
    options: {
      extractImages: true,
      extractTables: true
    }
  })
});
const { data: processedDoc } = await processResponse.json();

// 3. Save to history
await fetch('/api/history', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    metadata: processedDoc.metadata,
    markdownContent: processedDoc.markdownContent,
    jsonContent: processedDoc,
    tags: ['important', 'analysis']
  })
});

// 4. Export document
const exportResponse = await fetch('/api/export', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    documentId: processedDoc.id,
    format: 'html'
  })
});
const { data: exportData } = await exportResponse.json();

// 5. Download exported file
window.open(exportData.downloadUrl, '_blank');
```

### Search and Filter History

```javascript
// Search for documents containing "quarterly report"
const searchResponse = await fetch('/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'quarterly report',
    searchIn: ['content', 'metadata']
  })
});

// Get history with filters
const historyResponse = await fetch('/api/history?' + new URLSearchParams({
  page: '1',
  pageSize: '20',
  fileType: 'pdf,docx',
  hasImages: 'true',
  sortBy: 'uploadDate',
  sortOrder: 'desc'
}));
```

## Development Notes

- All APIs return mock data for development purposes
- In production, implement proper database storage
- Add authentication and authorization
- Implement real document processing engines
- Add proper error logging and monitoring
- Use cloud storage for file handling
- Implement proper search indexing (Elasticsearch)

## Support

For API support and questions, please refer to the technical documentation or contact the development team. 