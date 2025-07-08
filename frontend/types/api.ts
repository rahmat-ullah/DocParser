// API Request and Response Types for Document Parser Web Application

// ============================================================================
// CORE DATA SCHEMAS
// ============================================================================

export interface DocumentMetadata {
  id: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  uploadDate: Date;
  lastModified: Date;
  processingTime?: number;
}

export interface DocumentSection {
  id: string;
  title: string;
  content: string;
  startIndex: number;
  endIndex: number;
  level: number; // Heading level (1-6)
  type: 'heading' | 'paragraph' | 'list' | 'table' | 'image' | 'math';
}

export interface ExtractedImage {
  id: string;
  index: number;
  page?: number; // For PDFs
  data: string; // Base64 encoded image data
  format: 'png' | 'jpeg' | 'jpg';
  width: number;
  height: number;
  description?: string; // AI-generated description
  bbox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface ExtractedTable {
  id: string;
  page?: number;
  data: string[][]; // 2D array of cell values
  headers?: string[];
  rows: number;
  cols: number;
  markdownTable: string;
  bbox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface MathExpression {
  id: string;
  expression: string;
  latex: string;
  type: 'inline' | 'block' | 'equation';
  startIndex: number;
  endIndex: number;
  page?: number;
}

export interface ParsedDocument {
  id: string;
  metadata: DocumentMetadata;
  originalContent: string;
  markdownContent: string;
  sections: DocumentSection[];
  images: ExtractedImage[];
  tables: ExtractedTable[];
  mathExpressions: MathExpression[];
  processingNotes?: string[];
  quality?: {
    ocrConfidence?: number;
    conversionAccuracy?: number;
    imageDescriptionQuality?: number;
  };
}

export interface ParsingProgress {
  stage: 'uploading' | 'parsing' | 'converting' | 'ai-processing' | 'complete' | 'error';
  progress: number; // 0-100
  message: string;
  details?: {
    currentStep?: string;
    totalSteps?: number;
    currentStepProgress?: number;
    estimatedTimeRemaining?: number;
  };
}

export interface DocumentHistoryEntry {
  id: string;
  metadata: DocumentMetadata;
  markdownContent: string;
  jsonContent: ParsedDocument;
  lastAccessed: Date;
  tags?: string[];
  notes?: string;
}

// ============================================================================
// API REQUEST TYPES
// ============================================================================

export interface UploadDocumentRequest {
  file: File;
  options?: {
    enableAI?: boolean;
    enableMathConversion?: boolean;
    enableTableExtraction?: boolean;
    quality?: 'fast' | 'balanced' | 'high';
  };
}

export interface ProcessDocumentRequest {
  fileId: string;
  fileName: string;
  fileType: string;
  options?: {
    enableAI?: boolean;
    enableMathConversion?: boolean;
    enableTableExtraction?: boolean;
    quality?: 'fast' | 'balanced' | 'high';
    customPrompt?: string; // For AI image descriptions
  };
}

export interface ExportRequest {
  documentId: string;
  format: 'markdown' | 'json' | 'html' | 'pdf';
  options?: {
    includeImages?: boolean;
    includeTables?: boolean;
    includeMath?: boolean;
    includeMetadata?: boolean;
  };
}

export interface UpdateDocumentRequest {
  documentId: string;
  markdownContent?: string;
  metadata?: Partial<DocumentMetadata>;
  tags?: string[];
  notes?: string;
}

export interface SearchRequest {
  query: string;
  documentId?: string;
  searchIn?: ('content' | 'metadata' | 'tags' | 'notes')[];
  options?: {
    caseSensitive?: boolean;
    wholeWords?: boolean;
    regex?: boolean;
  };
}

export interface BatchProcessRequest {
  files: File[];
  options?: {
    enableAI?: boolean;
    enableMathConversion?: boolean;
    enableTableExtraction?: boolean;
    quality?: 'fast' | 'balanced' | 'high';
  };
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: string;
    requestId: string;
    processingTime?: number;
  };
}

export interface UploadDocumentResponse {
  fileId: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  uploadUrl?: string; // For direct file access if needed
  processingJobId: string;
}

export interface ProcessDocumentResponse {
  document: ParsedDocument;
  processingStats: {
    totalProcessingTime: number;
    parsingTime: number;
    aiProcessingTime?: number;
    conversionTime: number;
  };
  warnings?: string[];
}

export interface ProgressResponse {
  jobId: string;
  progress: ParsingProgress;
  estimatedCompletion?: string;
}

export interface ExportResponse {
  downloadUrl: string;
  fileName: string;
  fileSize: number;
  format: string;
  expiresAt: string; // Download link expiration
}

export interface SearchResponse {
  results: SearchResult[];
  totalMatches: number;
  searchTime: number;
  query: string;
}

export interface SearchResult {
  documentId: string;
  fileName: string;
  matches: {
    type: 'content' | 'metadata' | 'tags' | 'notes';
    text: string;
    context: string;
    position?: {
      line: number;
      column: number;
    };
    confidence?: number;
  }[];
}

export interface HistoryResponse {
  documents: DocumentHistoryEntry[];
  totalCount: number;
  page?: number;
  pageSize?: number;
}

export interface BatchProcessResponse {
  jobId: string;
  totalFiles: number;
  processedFiles: number;
  results: (ProcessDocumentResponse | { error: string })[];
  overallProgress: number;
}

// ============================================================================
// WEBSOCKET MESSAGE TYPES
// ============================================================================

export interface WebSocketMessage {
  type: 'progress' | 'complete' | 'error' | 'cancel';
  jobId: string;
  data: any;
  timestamp: string;
}

export interface ProgressMessage extends WebSocketMessage {
  type: 'progress';
  data: ParsingProgress;
}

export interface CompleteMessage extends WebSocketMessage {
  type: 'complete';
  data: ProcessDocumentResponse;
}

export interface ErrorMessage extends WebSocketMessage {
  type: 'error';
  data: {
    code: string;
    message: string;
    details?: any;
  };
}

// ============================================================================
// PROCESSING OPTIONS AND CONFIGURATIONS
// ============================================================================

export interface ProcessingConfiguration {
  ai: {
    enabled: boolean;
    provider: 'openai' | 'anthropic' | 'google';
    model: string;
    customPrompts?: {
      imageDescription?: string;
      tableExtraction?: string;
      mathConversion?: string;
    };
  };
  ocr: {
    enabled: boolean;
    provider: 'tesseract' | 'openai' | 'azure';
    language: string[];
    confidence?: number;
  };
  conversion: {
    preserveFormatting: boolean;
    includePageNumbers: boolean;
    includeHeaders: boolean;
    includeFooters: boolean;
    mathFormat: 'latex' | 'mathml' | 'plain';
    tableFormat: 'markdown' | 'html' | 'csv';
  };
  quality: {
    imageResolution: number;
    compressionLevel: number;
    ocrAccuracy: 'fast' | 'balanced' | 'high';
  };
}

// ============================================================================
// ERROR TYPES
// ============================================================================

export interface DocumentParsingError {
  code: 'UNSUPPORTED_FORMAT' | 'FILE_TOO_LARGE' | 'CORRUPTED_FILE' | 'AI_SERVICE_ERROR' | 'OCR_FAILED' | 'CONVERSION_ERROR' | 'TIMEOUT' | 'UNKNOWN';
  message: string;
  fileName?: string;
  fileType?: string;
  details?: {
    originalError?: string;
    suggestions?: string[];
  };
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type SupportedFileType = 'pdf' | 'docx' | 'xlsx' | 'pptx' | 'txt' | 'png' | 'jpg' | 'jpeg';

export type ProcessingStage = 'uploading' | 'validating' | 'parsing' | 'extracting' | 'ai-processing' | 'converting' | 'finalizing' | 'complete' | 'error';

export type ExportFormat = 'markdown' | 'json' | 'html' | 'pdf' | 'docx' | 'txt';

export type QualityLevel = 'fast' | 'balanced' | 'high';

export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface FilterParams {
  fileType?: SupportedFileType[];
  dateFrom?: string;
  dateTo?: string;
  tags?: string[];
  hasImages?: boolean;
  hasTables?: boolean;
  hasMath?: boolean;
} 