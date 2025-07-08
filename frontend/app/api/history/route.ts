import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import type { 
  ApiResponse, 
  HistoryResponse, 
  DocumentHistoryEntry,
  PaginationParams,
  FilterParams
} from '@/types/api';

// Mock history storage (in production, use a database)
let mockHistory: DocumentHistoryEntry[] = [
  {
    id: randomUUID(),
    metadata: {
      id: randomUUID(),
      fileName: 'sample-report.pdf',
      fileType: 'application/pdf',
      fileSize: 2048000,
      uploadDate: new Date('2024-01-15T10:30:00Z'),
      lastModified: new Date('2024-01-15T10:30:00Z'),
      processingTime: 5200
    },
    markdownContent: `# Sample Report

This is a sample PDF document that has been converted to markdown.

## Executive Summary

The document contains important information about the project.

### Key Findings

- Finding 1: Important discovery
- Finding 2: Another crucial point
- Finding 3: Final observation

## Data Analysis

| Metric | Value | Change |
|--------|--------|--------|
| Revenue | $1,000,000 | +15% |
| Users | 50,000 | +8% |
| Growth | 12% | +2% |

## Conclusion

The analysis shows positive trends across all metrics.`,
    jsonContent: {
      id: randomUUID(),
      metadata: {
        id: randomUUID(),
        fileName: 'sample-report.pdf',
        fileType: 'application/pdf',
        fileSize: 2048000,
        uploadDate: new Date('2024-01-15T10:30:00Z'),
        lastModified: new Date('2024-01-15T10:30:00Z'),
        processingTime: 5200
      },
      originalContent: 'Original PDF content...',
      markdownContent: 'Markdown content...',
      sections: [],
      images: [],
      tables: [
        {
          id: randomUUID(),
          data: [['Metric', 'Value', 'Change'], ['Revenue', '$1,000,000', '+15%']],
          headers: ['Metric', 'Value', 'Change'],
          rows: 2,
          cols: 3,
          markdownTable: '| Metric | Value | Change |\n|--------|--------|\n| Revenue | $1,000,000 | +15% |'
        }
      ],
      mathExpressions: []
    },
    lastAccessed: new Date('2024-01-15T14:20:00Z'),
    tags: ['report', 'analysis', 'quarterly'],
    notes: 'Q4 financial report with key metrics'
  },
  {
    id: randomUUID(),
    metadata: {
      id: randomUUID(),
      fileName: 'presentation.pptx',
      fileType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      fileSize: 5120000,
      uploadDate: new Date('2024-01-14T09:15:00Z'),
      lastModified: new Date('2024-01-14T09:15:00Z'),
      processingTime: 8500
    },
    markdownContent: `# Project Presentation

## Slide 1: Introduction

Welcome to our project presentation.

## Slide 2: Objectives

- Objective 1: Increase efficiency
- Objective 2: Reduce costs
- Objective 3: Improve quality

## Slide 3: Results

![Chart showing results](chart.png)

The results exceeded expectations.`,
    jsonContent: {
      id: randomUUID(),
      metadata: {
        id: randomUUID(),
        fileName: 'presentation.pptx',
        fileType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        fileSize: 5120000,
        uploadDate: new Date('2024-01-14T09:15:00Z'),
        lastModified: new Date('2024-01-14T09:15:00Z'),
        processingTime: 8500
      },
      originalContent: 'Original PPTX content...',
      markdownContent: 'Markdown content...',
      sections: [],
      images: [
        {
          id: randomUUID(),
          index: 0,
          data: 'base64-chart-data',
          format: 'png',
          width: 800,
          height: 600,
          description: 'Chart showing project results'
        }
      ],
      tables: [],
      mathExpressions: []
    },
    lastAccessed: new Date('2024-01-14T16:45:00Z'),
    tags: ['presentation', 'project', 'results'],
    notes: 'Project kickoff presentation'
  }
];

function applyFilters(history: DocumentHistoryEntry[], filters: FilterParams): DocumentHistoryEntry[] {
  let filtered = [...history];

  if (filters.fileType && filters.fileType.length > 0) {
    filtered = filtered.filter(entry => 
      filters.fileType!.some(type => entry.metadata.fileType.includes(type))
    );
  }

  if (filters.dateFrom) {
    const fromDate = new Date(filters.dateFrom);
    filtered = filtered.filter(entry => 
      new Date(entry.metadata.uploadDate) >= fromDate
    );
  }

  if (filters.dateTo) {
    const toDate = new Date(filters.dateTo);
    filtered = filtered.filter(entry => 
      new Date(entry.metadata.uploadDate) <= toDate
    );
  }

  if (filters.tags && filters.tags.length > 0) {
    filtered = filtered.filter(entry => 
      entry.tags && entry.tags.some(tag => filters.tags!.includes(tag))
    );
  }

  if (filters.hasImages !== undefined) {
    filtered = filtered.filter(entry => 
      (entry.jsonContent.images && entry.jsonContent.images.length > 0) === filters.hasImages
    );
  }

  if (filters.hasTables !== undefined) {
    filtered = filtered.filter(entry => 
      (entry.jsonContent.tables && entry.jsonContent.tables.length > 0) === filters.hasTables
    );
  }

  if (filters.hasMath !== undefined) {
    filtered = filtered.filter(entry => 
      (entry.jsonContent.mathExpressions && entry.jsonContent.mathExpressions.length > 0) === filters.hasMath
    );
  }

  return filtered;
}

function applySorting(history: DocumentHistoryEntry[], sortBy?: string, sortOrder: 'asc' | 'desc' = 'desc'): DocumentHistoryEntry[] {
  const sorted = [...history];

  switch (sortBy) {
    case 'fileName':
      sorted.sort((a, b) => {
        const comparison = a.metadata.fileName.localeCompare(b.metadata.fileName);
        return sortOrder === 'asc' ? comparison : -comparison;
      });
      break;
    case 'fileSize':
      sorted.sort((a, b) => {
        const comparison = a.metadata.fileSize - b.metadata.fileSize;
        return sortOrder === 'asc' ? comparison : -comparison;
      });
      break;
    case 'uploadDate':
      sorted.sort((a, b) => {
        const comparison = new Date(a.metadata.uploadDate).getTime() - new Date(b.metadata.uploadDate).getTime();
        return sortOrder === 'asc' ? comparison : -comparison;
      });
      break;
    case 'lastAccessed':
    default:
      sorted.sort((a, b) => {
        const comparison = new Date(a.lastAccessed).getTime() - new Date(b.lastAccessed).getTime();
        return sortOrder === 'asc' ? comparison : -comparison;
      });
      break;
  }

  return sorted;
}

// GET /api/history - Retrieve document history with filtering and pagination
export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<HistoryResponse>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    const { searchParams } = new URL(request.url);
    
    // Parse pagination parameters
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = Math.min(parseInt(searchParams.get('pageSize') || '20'), 100); // Max 100 items per page
    const sortBy = searchParams.get('sortBy') || 'lastAccessed';
    const sortOrder = (searchParams.get('sortOrder') || 'desc') as 'asc' | 'desc';

    // Parse filter parameters
    const filters: FilterParams = {
      fileType: searchParams.get('fileType')?.split(',') as any[],
      dateFrom: searchParams.get('dateFrom') || undefined,
      dateTo: searchParams.get('dateTo') || undefined,
      tags: searchParams.get('tags')?.split(','),
      hasImages: searchParams.get('hasImages') ? searchParams.get('hasImages') === 'true' : undefined,
      hasTables: searchParams.get('hasTables') ? searchParams.get('hasTables') === 'true' : undefined,
      hasMath: searchParams.get('hasMath') ? searchParams.get('hasMath') === 'true' : undefined,
    };

    // Apply filters
    let filteredHistory = applyFilters(mockHistory, filters);
    
    // Apply sorting
    filteredHistory = applySorting(filteredHistory, sortBy, sortOrder);

    // Apply pagination
    const totalCount = filteredHistory.length;
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedHistory = filteredHistory.slice(startIndex, endIndex);

    return NextResponse.json({
      success: true,
      data: {
        documents: paginatedHistory,
        totalCount,
        page,
        pageSize
      },
      metadata: {
        timestamp,
        requestId,
        processingTime: Date.now() - new Date(timestamp).getTime()
      }
    });

  } catch (error) {
    console.error('History retrieval error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'HISTORY_ERROR',
        message: 'Failed to retrieve document history.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
}

// POST /api/history - Add or update document in history
export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<DocumentHistoryEntry>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    const body: Partial<DocumentHistoryEntry> = await request.json();
    
    if (!body.metadata || !body.markdownContent || !body.jsonContent) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'MISSING_PARAMETERS',
          message: 'Missing required parameters: metadata, markdownContent, and jsonContent are required.',
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    const historyEntry: DocumentHistoryEntry = {
      id: body.id || randomUUID(),
      metadata: body.metadata,
      markdownContent: body.markdownContent,
      jsonContent: body.jsonContent,
      lastAccessed: new Date(),
      tags: body.tags || [],
      notes: body.notes || ''
    };

    // Check if entry already exists
    const existingIndex = mockHistory.findIndex(entry => entry.id === historyEntry.id);
    
    if (existingIndex >= 0) {
      // Update existing entry
      mockHistory[existingIndex] = historyEntry;
    } else {
      // Add new entry to the beginning
      mockHistory.unshift(historyEntry);
      
      // Keep only the last 100 entries
      if (mockHistory.length > 100) {
        mockHistory = mockHistory.slice(0, 100);
      }
    }

    return NextResponse.json({
      success: true,
      data: historyEntry,
      metadata: {
        timestamp,
        requestId,
        processingTime: Date.now() - new Date(timestamp).getTime()
      }
    });

  } catch (error) {
    console.error('History save error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'HISTORY_SAVE_ERROR',
        message: 'Failed to save document to history.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
}

// DELETE /api/history - Clear history or delete specific documents
export async function DELETE(request: NextRequest): Promise<NextResponse<ApiResponse<{ deletedCount: number }>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    const { searchParams } = new URL(request.url);
    const documentId = searchParams.get('documentId');
    
    if (documentId) {
      // Delete specific document
      const initialLength = mockHistory.length;
      mockHistory = mockHistory.filter(entry => entry.id !== documentId);
      const deletedCount = initialLength - mockHistory.length;
      
      if (deletedCount === 0) {
        return NextResponse.json({
          success: false,
          error: {
            code: 'DOCUMENT_NOT_FOUND',
            message: 'Document not found in history.',
            details: { documentId }
          },
          metadata: { timestamp, requestId }
        }, { status: 404 });
      }
      
      return NextResponse.json({
        success: true,
        data: { deletedCount },
        metadata: {
          timestamp,
          requestId,
          processingTime: Date.now() - new Date(timestamp).getTime()
        }
      });
    } else {
      // Clear all history
      const deletedCount = mockHistory.length;
      mockHistory = [];
      
      return NextResponse.json({
        success: true,
        data: { deletedCount },
        metadata: {
          timestamp,
          requestId,
          processingTime: Date.now() - new Date(timestamp).getTime()
        }
      });
    }

  } catch (error) {
    console.error('History deletion error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'HISTORY_DELETE_ERROR',
        message: 'Failed to delete from history.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
} 