import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { randomUUID } from 'crypto';
import type { 
  ApiResponse, 
  UploadDocumentResponse, 
  DocumentParsingError,
  SupportedFileType 
} from '@/types/api';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const SUPPORTED_TYPES: SupportedFileType[] = ['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'png', 'jpg', 'jpeg'];

function validateFileType(fileName: string): SupportedFileType | null {
  const extension = fileName.split('.').pop()?.toLowerCase();
  return SUPPORTED_TYPES.includes(extension as SupportedFileType) 
    ? extension as SupportedFileType 
    : null;
}

export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<UploadDocumentResponse>>> {
  const requestId = randomUUID();
  const timestamp = new Date().toISOString();
  
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const optionsStr = formData.get('options') as string | null;
    
    // Parse options if provided
    let options = {};
    if (optionsStr) {
      try {
        options = JSON.parse(optionsStr);
      } catch {
        return NextResponse.json({
          success: false,
          error: {
            code: 'INVALID_OPTIONS',
            message: 'Invalid options format. Must be valid JSON.',
          },
          metadata: { timestamp, requestId }
        }, { status: 400 });
      }
    }

    if (!file) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'NO_FILE',
          message: 'No file provided in the request.',
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'FILE_TOO_LARGE',
          message: `File size (${Math.round(file.size / 1024 / 1024)}MB) exceeds maximum allowed size of ${MAX_FILE_SIZE / 1024 / 1024}MB.`,
          details: {
            fileSize: file.size,
            maxSize: MAX_FILE_SIZE
          }
        },
        metadata: { timestamp, requestId }
      }, { status: 413 });
    }

    // Validate file type
    const fileType = validateFileType(file.name);
    if (!fileType) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'UNSUPPORTED_FORMAT',
          message: `File type not supported. Supported formats: ${SUPPORTED_TYPES.join(', ').toUpperCase()}`,
          details: {
            fileName: file.name,
            supportedTypes: SUPPORTED_TYPES
          }
        },
        metadata: { timestamp, requestId }
      }, { status: 400 });
    }

    // Generate unique file ID and save file
    const fileId = randomUUID();
    const fileName = `${fileId}_${file.name.replace(/[^a-zA-Z0-9.-]/g, '_')}`;
    const tempDir = join(process.cwd(), 'temp');
    
    // Ensure temp directory exists
    await require('fs/promises').mkdir(tempDir, { recursive: true });
    
    const filePath = join(tempDir, fileName);
    const buffer = new Uint8Array(await file.arrayBuffer());
    await writeFile(filePath, buffer);

    // Generate processing job ID
    const processingJobId = randomUUID();

    // Store job metadata (in production, use a proper job queue/database)
    const jobMetadata = {
      jobId: processingJobId,
      fileId,
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size,
      filePath,
      options,
      status: 'pending',
      createdAt: timestamp,
      requestId
    };

    // In production, store this in Redis/Database
    // For now, we'll store it in memory or local storage
    console.log('Job created:', jobMetadata);

    return NextResponse.json({
      success: true,
      data: {
        fileId,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        processingJobId,
        uploadUrl: `/temp/${fileName}` // For potential direct access
      },
      metadata: {
        timestamp,
        requestId,
        processingTime: Date.now() - new Date(timestamp).getTime()
      }
    });

  } catch (error) {
    console.error('Upload error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'UPLOAD_ERROR',
        message: 'Failed to upload file due to server error.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      metadata: { timestamp, requestId }
    }, { status: 500 });
  }
}

export async function GET(): Promise<NextResponse<ApiResponse<{ maxFileSize: number; supportedTypes: SupportedFileType[] }>>> {
  return NextResponse.json({
    success: true,
    data: {
      maxFileSize: MAX_FILE_SIZE,
      supportedTypes: SUPPORTED_TYPES
    },
    metadata: {
      timestamp: new Date().toISOString(),
      requestId: randomUUID()
    }
  });
} 