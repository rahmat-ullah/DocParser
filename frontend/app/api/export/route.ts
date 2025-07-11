import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import type { 
  ApiResponse, 
  ExportResponse, 
  ExportRequest,
  ExportFormat 
} from '@/types/api';

// Utility function to generate export content based on format
function generateExportContent(document: any, format: ExportFormat, options: any = {}): { content: string | Buffer; mimeType: string; extension: string } {
  const { 
    includeImages = true, 
    includeTables = true, 
    includeMath = true, 
    includeMetadata = true 
  } = options;

  switch (format) {
    case 'markdown': {
      let content = document.markdownContent || '';
      
      if (includeMetadata) {
        const metadata = `---
title: ${document.metadata?.fileName || 'Untitled'}
created: ${document.metadata?.uploadDate || new Date().toISOString()}
fileType: ${document.metadata?.fileType || 'unknown'}
fileSize: ${document.metadata?.fileSize || 0}
---

`;
        content = metadata + content;
      }

      if (!includeImages) {
        content = content.replace(/!\[.*?\]\(.*?\)/g, '[Image removed]');
      }

      if (!includeTables) {
        content = content.replace(/\|.*\|/g, '[Table removed]');
      }

      if (!includeMath) {
        content = content.replace(/\$\$.*?\$\$/g, '[Math equation removed]');
        content = content.replace(/\$.*?\$/g, '[Math removed]');
      }

      return {
        content,
        mimeType: 'text/markdown',
        extension: 'md'
      };
    }

    case 'json': {
      const jsonData = {
        ...document,
        exportOptions: options,
        exportedAt: new Date().toISOString()
      };

      if (!includeImages) {
        delete jsonData.images;
      }

      if (!includeTables) {
        delete jsonData.tables;
      }

      if (!includeMath) {
        delete jsonData.mathExpressions;
      }

      if (!includeMetadata) {
        delete jsonData.metadata;
      }

      return {
        content: JSON.stringify(jsonData, null, 2),
        mimeType: 'application/json',
        extension: 'json'
      };
    }

    case 'html': {
      // Convert markdown to HTML (simplified)
      let htmlContent = document.markdownContent || '';
      
      // Basic markdown to HTML conversion
      htmlContent = htmlContent
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/!\[([^\]]*)\]\(([^)]*)\)/gim, '<img alt="$1" src="$2" />')
        .replace(/\[([^\]]*)\]\(([^)]*)\)/gim, '<a href="$2">$1</a>')
        .replace(/\n/gim, '<br>');

      const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${document.metadata?.fileName || 'Exported Document'}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #1a237e; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    ${includeMetadata ? `<div class="metadata">
        <h1>${document.metadata?.fileName || 'Untitled'}</h1>
        <p><strong>File Type:</strong> ${document.metadata?.fileType || 'Unknown'}</p>
        <p><strong>Created:</strong> ${document.metadata?.uploadDate || 'Unknown'}</p>
        <p><strong>File Size:</strong> ${document.metadata?.fileSize ? Math.round(document.metadata.fileSize / 1024) + 'KB' : 'Unknown'}</p>
        <hr>
    </div>` : ''}
    <div class="content">
        ${htmlContent}
    </div>
</body>
</html>`;

      return {
        content: fullHtml,
        mimeType: 'text/html',
        extension: 'html'
      };
    }

    case 'txt': {
      // Strip markdown formatting for plain text
      let txtContent = document.markdownContent || '';
      
      txtContent = txtContent
        .replace(/#{1,6}\s*/g, '') // Remove headers
        .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
        .replace(/\*(.*?)\*/g, '$1') // Remove italic
        .replace(/!\[.*?\]\(.*?\)/g, '[Image]') // Replace images
        .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1') // Remove links, keep text
        .replace(/\|.*\|/g, '[Table]'); // Replace tables

      if (includeMetadata) {
        const metadata = `Document: ${document.metadata?.fileName || 'Untitled'}
File Type: ${document.metadata?.fileType || 'Unknown'}
Created: ${document.metadata?.uploadDate || 'Unknown'}
File Size: ${document.metadata?.fileSize ? Math.round(document.metadata.fileSize / 1024) + 'KB' : 'Unknown'}

---

`;
        txtContent = metadata + txtContent;
      }

      return {
        content: txtContent,
        mimeType: 'text/plain',
        extension: 'txt'
      };
    }

    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<ExportResponse>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    const body: ExportRequest = await request.json();
    const { documentId, format, options = {} } = body;

    if (!documentId || !format) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'MISSING_PARAMETERS',
          message: 'Missing required parameters: documentId and format are required.',
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    // Validate export format
    const supportedFormats: ExportFormat[] = ['markdown', 'json', 'html', 'txt'];
    if (!supportedFormats.includes(format)) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'UNSUPPORTED_FORMAT',
          message: `Export format '${format}' is not supported. Supported formats: ${supportedFormats.join(', ')}`,
          details: { supportedFormats }
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    // In production, this would fetch the document from a database
    // For now, we'll use mock data or retrieve from client storage
    const mockDocument = {
      id: documentId,
      metadata: {
        fileName: 'sample-document.pdf',
        fileType: 'application/pdf',
        fileSize: 1024000,
        uploadDate: new Date().toISOString(),
        lastModified: new Date().toISOString()
      },
      markdownContent: `# Sample Document

This is a sample document that has been converted to markdown.

## Features

- Text extraction
- Image processing
- Table conversion

### Table Example

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

### Math Example

The equation $E = mc^2$ is famous.

$$\\sum_{i=1}^n i = \\frac{n(n+1)}{2}$$

![Sample Image](sample-image.png)

## Conclusion

Document processing completed successfully.`,
      markdownUrl: `/api/documents/${documentId}/markdown`,
      images: [
        {
          id: randomUUID(),
          index: 0,
          data: 'base64-image-data',
          format: 'png',
          width: 800,
          height: 600,
          description: 'Sample image description'
        }
      ],
      tables: [
        {
          id: randomUUID(),
          data: [['Column 1', 'Column 2', 'Column 3'], ['Data 1', 'Data 2', 'Data 3']],
          headers: ['Column 1', 'Column 2', 'Column 3'],
          rows: 2,
          cols: 3,
          markdownTable: '| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |'
        }
      ],
      mathExpressions: [
        {
          id: randomUUID(),
          expression: 'E = mc²',
          latex: 'E = mc^2',
          type: 'inline',
          startIndex: 0,
          endIndex: 6
        }
      ]
    };

    // Generate export content
    const { content, mimeType, extension } = generateExportContent(mockDocument, format, options);
    
    // In production, save the file to cloud storage (S3, etc.) and return a download URL
    // For now, we'll create a data URL
    const fileName = `${mockDocument.metadata.fileName.replace(/\.[^/.]+$/, '')}_export.${extension}`;
    const fileSize = Buffer.byteLength(content.toString(), 'utf8');
    
    // Create a temporary download URL (in production, use cloud storage)
    const downloadUrl = `data:${mimeType};base64,${Buffer.from(content.toString()).toString('base64')}`;
    
    // Set expiration time (24 hours from now)
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();

    return NextResponse.json({
      success: true,
      data: {
        downloadUrl,
        fileName,
        fileSize,
        format,
        expiresAt
      },
      metadata: {
        timestamp,
        requestId,
        processingTime: Date.now() - new Date(timestamp).getTime()
      }
    });

  } catch (error) {
    console.error('Export error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'EXPORT_ERROR',
        message: 'Failed to export document due to server error.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
}

// Get available export formats
export async function GET(): Promise<NextResponse<ApiResponse<{ formats: ExportFormat[] }>>> {
  return NextResponse.json({
    success: true,
    data: {
      formats: ['markdown', 'json', 'html', 'txt']
    },
    metadata: {
      timestamp: new Date().toISOString(),
      requestId: randomUUID()
    }
  });
} 