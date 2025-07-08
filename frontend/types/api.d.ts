import { z } from "zod";

// ============================================================================
// ZOD SCHEMAS FOR API VALIDATION
// ============================================================================

// Document metadata schema
const DocumentMetadataSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.string(),
  size: z.number(),
  uploadDate: z.date(),
  lastModified: z.date(),
});

// Document section schema
const DocumentSectionSchema = z.object({
  id: z.string(),
  title: z.string(),
  content: z.string(),
  startIndex: z.number(),
  endIndex: z.number(),
  level: z.number(),
});

// Parsed document schema
const ParsedDocumentSchema = z.object({
  id: z.string(),
  metadata: DocumentMetadataSchema,
  originalContent: z.string(),
  markdownContent: z.string(),
  sections: z.array(DocumentSectionSchema),
});

// ============================================================================
// POST /api/upload ENDPOINT
// ============================================================================

// Upload request schema (for validation)
const UploadRequestSchema = z.object({
  // Note: File validation would be handled separately in multipart/form-data
  // This is for any additional metadata sent with the upload
  metadata: z.object({
    originalName: z.string(),
    size: z.number(),
    type: z.string(),
  }).optional(),
  options: z.object({
    enableAI: z.boolean().optional(),
    enableMathConversion: z.boolean().optional(),
    enableTableExtraction: z.boolean().optional(),
    quality: z.enum(['fast', 'balanced', 'high']).optional(),
  }).optional(),
});

// Upload response schema
const UploadResponseSchema = z.object({
  fileId: z.string(),
});

// ============================================================================
// POST /api/process ENDPOINT
// ============================================================================

// Process request schema
const ProcessRequestSchema = z.object({
  fileId: z.string(),
  options: z.object({
    enableAI: z.boolean().optional(),
    enableMathConversion: z.boolean().optional(),
    enableTableExtraction: z.boolean().optional(),
    quality: z.enum(['fast', 'balanced', 'high']).optional(),
    customPrompt: z.string().optional(),
  }).optional(),
});

// Process stream response schema (for streaming updates)
const ProcessStreamResponseSchema = z.object({
  stage: z.enum(['uploading', 'parsing', 'converting', 'ai-processing', 'complete', 'error']),
  percent: z.number().min(0).max(100),
  message: z.string(),
  details: z.object({
    currentStep: z.string().optional(),
    totalSteps: z.number().optional(),
    currentStepProgress: z.number().optional(),
    estimatedTimeRemaining: z.number().optional(),
  }).optional(),
});

// Process final response schema (when processing is complete)
const ProcessFinalResponseSchema = z.object({
  document: ParsedDocumentSchema,
  processingStats: z.object({
    totalProcessingTime: z.number(),
    parsingTime: z.number(),
    aiProcessingTime: z.number().optional(),
    conversionTime: z.number(),
  }),
  warnings: z.array(z.string()).optional(),
});

// ============================================================================
// TYPESCRIPT TYPES (AUTO-GENERATED FROM ZOD SCHEMAS)
// ============================================================================

// Base types
export type DocumentMetadata = z.infer<typeof DocumentMetadataSchema>;
export type DocumentSection = z.infer<typeof DocumentSectionSchema>;
export type ParsedDocument = z.infer<typeof ParsedDocumentSchema>;

// Upload endpoint types
export type UploadRequest = z.infer<typeof UploadRequestSchema>;
export type UploadResponse = z.infer<typeof UploadResponseSchema>;

// Process endpoint types
export type ProcessRequest = z.infer<typeof ProcessRequestSchema>;
export type ProcessStreamResponse = z.infer<typeof ProcessStreamResponseSchema>;
export type ProcessFinalResponse = z.infer<typeof ProcessFinalResponseSchema>;

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

// Upload endpoint validation
export const validateUploadRequest = (data: unknown): UploadRequest => {
  return UploadRequestSchema.parse(data);
};

export const validateUploadResponse = (data: unknown): UploadResponse => {
  return UploadResponseSchema.parse(data);
};

// Process endpoint validation
export const validateProcessRequest = (data: unknown): ProcessRequest => {
  return ProcessRequestSchema.parse(data);
};

export const validateProcessStreamResponse = (data: unknown): ProcessStreamResponse => {
  return ProcessStreamResponseSchema.parse(data);
};

export const validateProcessFinalResponse = (data: unknown): ProcessFinalResponse => {
  return ProcessFinalResponseSchema.parse(data);
};

// ============================================================================
// OPENAPI SPECIFICATION HELPERS
// ============================================================================

// Helper function to generate OpenAPI schema from Zod schema
// Note: You would need to install 'zod-to-openapi' for full OpenAPI generation
export const schemas = {
  UploadRequest: UploadRequestSchema,
  UploadResponse: UploadResponseSchema,
  ProcessRequest: ProcessRequestSchema,
  ProcessStreamResponse: ProcessStreamResponseSchema,
  ProcessFinalResponse: ProcessFinalResponseSchema,
  DocumentMetadata: DocumentMetadataSchema,
  DocumentSection: DocumentSectionSchema,
  ParsedDocument: ParsedDocumentSchema,
};

// ============================================================================
// API ENDPOINT SPECIFICATIONS
// ============================================================================

/**
 * OpenAPI 3.0 Specification for Document Processing API
 * 
 * POST /api/upload
 * Content-Type: multipart/form-data
 * Request Body:
 *   - file: File (required)
 *   - metadata: JSON string (optional)
 *   - options: JSON string (optional)
 * Response: { fileId: string }
 * 
 * POST /api/process
 * Content-Type: application/json
 * Request Body: { fileId: string, options?: ProcessOptions }
 * Response: Server-Sent Events stream
 *   - Stream: { stage, percent, message, details? }
 *   - Final: { document, processingStats, warnings? }
 */

// Type guards for runtime type checking
export const isProcessStreamResponse = (data: unknown): data is ProcessStreamResponse => {
  return ProcessStreamResponseSchema.safeParse(data).success;
};

export const isProcessFinalResponse = (data: unknown): data is ProcessFinalResponse => {
  return ProcessFinalResponseSchema.safeParse(data).success;
};

// ============================================================================
// ERROR HANDLING
// ============================================================================

const ApiErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  details: z.unknown().optional(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;

export const validateApiError = (data: unknown): ApiError => {
  return ApiErrorSchema.parse(data);
};

// Common API error codes
export const API_ERROR_CODES = {
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  PROCESSING_FAILED: 'PROCESSING_FAILED',
  FILE_NOT_FOUND: 'FILE_NOT_FOUND',
  INVALID_REQUEST: 'INVALID_REQUEST',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
} as const;

export type ApiErrorCode = keyof typeof API_ERROR_CODES;
