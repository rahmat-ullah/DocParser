import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import type { 
  ApiResponse, 
  SearchResponse, 
  SearchRequest,
  SearchResult
} from '@/types/api';

// Mock document data for search (in production, use a search engine like Elasticsearch)
const mockDocuments = [
  {
    id: randomUUID(),
    fileName: 'project-report.pdf',
    content: `# Project Report Q4 2024

## Executive Summary

Our quarterly analysis shows significant growth in user engagement and revenue. The new features launched in October have been well-received by users, leading to a 25% increase in daily active users.

## Key Metrics

- Revenue: $2,500,000 (+18% QoQ)
- Active Users: 125,000 (+25% QoQ) 
- Customer Satisfaction: 4.2/5 (+0.3 points)
- Feature Adoption: 78% (+15% QoQ)

## Analysis

The machine learning algorithms implemented for recommendation systems have significantly improved user experience. Data analytics reveal that users spend 40% more time on the platform compared to Q3.

### Revenue Breakdown

Product sales contributed to 60% of total revenue, while subscription services accounted for 35%. The remaining 5% came from premium features and add-ons.

## Recommendations

1. Continue investing in machine learning capabilities
2. Expand the recommendation system to more product categories
3. Focus on mobile app optimization for better user engagement
4. Implement advanced analytics dashboard for business users

## Conclusion

The quarter exceeded expectations across all key performance indicators. The focus on data-driven decision making and user experience optimization has proven successful.`,
    metadata: {
      tags: ['report', 'quarterly', 'analysis', 'revenue', 'metrics'],
      uploadDate: '2024-01-15T10:30:00Z',
      fileType: 'application/pdf'
    }
  },
  {
    id: randomUUID(),
    fileName: 'technical-documentation.docx',
    content: `# API Documentation

## Authentication

All API endpoints require authentication using Bearer tokens. Include the token in the Authorization header:

\`\`\`
Authorization: Bearer your-api-token-here
\`\`\`

## Endpoints

### Document Processing

POST /api/process
- Upload and process documents
- Supports PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG
- Returns parsed content in markdown format

### Machine Learning Features

GET /api/ml/analyze
- Perform content analysis using AI
- Extract entities, sentiment, and key topics
- Requires premium subscription

### User Management

POST /api/users
- Create new user accounts
- Validate email and password requirements
- Send welcome email notification

## Error Handling

The API uses standard HTTP status codes and returns JSON error responses:

\`\`\`json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required parameter: file"
  }
}
\`\`\`

## Rate Limiting

- 1000 requests per hour for authenticated users
- 100 requests per hour for anonymous users
- Premium users have higher limits

## Data Analytics

All API calls are logged for analytics and monitoring. We track:
- Response times
- Error rates  
- Usage patterns
- Performance metrics`,
    metadata: {
      tags: ['documentation', 'api', 'technical', 'authentication', 'machine learning'],
      uploadDate: '2024-01-12T14:20:00Z',
      fileType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
  },
  {
    id: randomUUID(),
    fileName: 'user-feedback.txt',
    content: `User Feedback Collection - January 2024

Positive Feedback:
- "The new machine learning features are amazing! The document analysis saves me hours of work." - Sarah M.
- "Love the improved user interface. Much more intuitive than before." - Mike D.
- "Analytics dashboard provides exactly what I need for reporting." - Jennifer K.
- "Fast processing times even for large documents." - David L.

Areas for Improvement:
- "Would like more export formats, especially PowerPoint." - Lisa R.
- "Mobile app could use better offline capabilities." - Tom W.
- "Pricing for premium features seems high for small businesses." - Alex C.
- "Need better integration with other business tools." - Rachel S.

Feature Requests:
- Batch processing for multiple documents
- Advanced search within processed documents
- Collaboration features for team projects
- API access for enterprise customers
- Custom templates for different document types

Common Issues:
- Occasional timeout errors during peak hours
- Some PDF files with complex layouts not parsing correctly
- Memory usage spikes with very large files
- Inconsistent performance across different browsers

Overall Satisfaction: 4.2/5 stars
Total Responses: 847
Response Rate: 23.4%

Action Items:
1. Investigate PDF parsing issues with complex layouts
2. Research additional export format options
3. Develop mobile app offline capabilities
4. Review pricing strategy for small business segment
5. Plan API development for enterprise features`,
    metadata: {
      tags: ['feedback', 'user experience', 'improvement', 'analytics', 'satisfaction'],
      uploadDate: '2024-01-10T09:45:00Z',
      fileType: 'text/plain'
    }
  }
];

function performSearch(query: string, searchIn: string[] = ['content'], options: any = {}): SearchResult[] {
  const results: SearchResult[] = [];
  const { caseSensitive = false, wholeWords = false, regex = false } = options;
  
  let searchPattern: RegExp;
  
  try {
    if (regex) {
      searchPattern = new RegExp(query, caseSensitive ? 'g' : 'gi');
    } else {
      const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = wholeWords ? `\\b${escapedQuery}\\b` : escapedQuery;
      searchPattern = new RegExp(pattern, caseSensitive ? 'g' : 'gi');
    }
  } catch (error) {
    // Invalid regex pattern
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    searchPattern = new RegExp(escapedQuery, caseSensitive ? 'g' : 'gi');
  }

  for (const doc of mockDocuments) {
    const matches: SearchResult['matches'] = [];

    // Search in content
    if (searchIn.includes('content')) {
      const contentMatches = Array.from(doc.content.matchAll(searchPattern));
      for (const match of contentMatches) {
        const startIndex = match.index || 0;
        const contextStart = Math.max(0, startIndex - 50);
        const contextEnd = Math.min(doc.content.length, startIndex + match[0].length + 50);
        const context = doc.content.substring(contextStart, contextEnd);
        
        // Calculate line number
        const textBeforeMatch = doc.content.substring(0, startIndex);
        const lineNumber = textBeforeMatch.split('\n').length;
        
        matches.push({
          type: 'content',
          text: match[0],
          context: context.replace(/\n/g, ' ').trim(),
          position: {
            line: lineNumber,
            column: startIndex - textBeforeMatch.lastIndexOf('\n')
          },
          confidence: 0.9
        });
      }
    }

    // Search in metadata (tags, filename)
    if (searchIn.includes('metadata')) {
      // Search in filename
      const filenameMatches = Array.from(doc.fileName.matchAll(searchPattern));
      for (const match of filenameMatches) {
        matches.push({
          type: 'metadata',
          text: match[0],
          context: `Filename: ${doc.fileName}`,
          confidence: 0.95
        });
      }

      // Search in tags
      if (doc.metadata.tags) {
        for (const tag of doc.metadata.tags) {
          const tagMatches = Array.from(tag.matchAll(searchPattern));
          for (const match of tagMatches) {
            matches.push({
              type: 'metadata',
              text: match[0],
              context: `Tag: ${tag}`,
              confidence: 0.8
            });
          }
        }
      }
    }

    if (matches.length > 0) {
      results.push({
        documentId: doc.id,
        fileName: doc.fileName,
        matches: matches.slice(0, 10) // Limit to 10 matches per document
      });
    }
  }

  // Sort results by relevance (number of matches and confidence)
  results.sort((a, b) => {
    const aScore = a.matches.reduce((sum, match) => sum + (match.confidence || 0), 0);
    const bScore = b.matches.reduce((sum, match) => sum + (match.confidence || 0), 0);
    return bScore - aScore;
  });

  return results.slice(0, 50); // Limit to 50 results
}

// POST /api/search - Perform search across documents
export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<SearchResponse>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  const startTime = Date.now();
  
  try {
    const body: SearchRequest = await request.json();
    const { query, documentId, searchIn = ['content'], options = {} } = body;

    if (!query || query.trim().length === 0) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'MISSING_QUERY',
          message: 'Search query is required and cannot be empty.',
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    if (query.length > 500) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'QUERY_TOO_LONG',
          message: 'Search query cannot exceed 500 characters.',
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    // If documentId is specified, filter to that document only
    let documentsToSearch = mockDocuments;
    if (documentId) {
      documentsToSearch = mockDocuments.filter(doc => doc.id === documentId);
      if (documentsToSearch.length === 0) {
        return NextResponse.json({
          success: false,
          error: {
            code: 'DOCUMENT_NOT_FOUND',
            message: 'Specified document not found.',
            details: { documentId }
          },
          metadata: { timestamp, requestId }
        }, { status: 404 });
      }
    }

    // Temporarily override mockDocuments for search
    const originalMockDocuments = mockDocuments;
    (global as any).mockDocuments = documentsToSearch;

    // Perform the search
    const results = performSearch(query, searchIn, options);
    const searchTime = Date.now() - startTime;
    const totalMatches = results.reduce((sum, result) => sum + result.matches.length, 0);

    // Restore original mockDocuments
    (global as any).mockDocuments = originalMockDocuments;

    return NextResponse.json({
      success: true,
      data: {
        results,
        totalMatches,
        searchTime,
        query: query.trim()
      },
      metadata: {
        timestamp,
        requestId,
        processingTime: searchTime
      }
    });

  } catch (error) {
    console.error('Search error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'SEARCH_ERROR',
        message: 'Failed to perform search due to server error.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
}

// GET /api/search - Get search suggestions or recent searches
export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<{ suggestions: string[]; recentSearches: string[] }>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    const { searchParams } = new URL(request.url);
    const prefix = searchParams.get('prefix');

    // Generate search suggestions based on content
    const suggestions: string[] = [];
    if (prefix && prefix.length >= 2) {
      const commonTerms = [
        'machine learning', 'analytics', 'revenue', 'user experience', 
        'documentation', 'authentication', 'performance', 'features',
        'analysis', 'metrics', 'feedback', 'improvement', 'api'
      ];
      
      suggestions.push(...commonTerms
        .filter(term => term.toLowerCase().includes(prefix.toLowerCase()))
        .slice(0, 10)
      );
    }

    // Mock recent searches (in production, store in user session/database)
    const recentSearches = [
      'machine learning',
      'revenue analysis',
      'user feedback',
      'api documentation',
      'performance metrics'
    ];

    return NextResponse.json({
      success: true,
      data: {
        suggestions,
        recentSearches: prefix ? [] : recentSearches
      },
      metadata: {
        timestamp,
        requestId,
        processingTime: Date.now() - new Date(timestamp).getTime()
      }
    });

  } catch (error) {
    console.error('Search suggestions error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'SEARCH_SUGGESTIONS_ERROR',
        message: 'Failed to retrieve search suggestions.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
} 