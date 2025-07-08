# Project Structure and Implementation Examples

## 1. Project Directory Structure

```
document-parser-app/
├── README.md
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── .env.local
├── .gitignore
├── public/
│   ├── favicon.ico
│   ├── icons/
│   └── sample-documents/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── api/
│   │       ├── upload/
│   │       │   └── route.ts
│   │       ├── process/
│   │       │   └── route.ts
│   │       ├── export/
│   │       │   └── route.ts
│   │       └── history/
│   │           └── route.ts
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── toast.tsx
│   │   │   └── dialog.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── document/
│   │   │   ├── DocumentViewer.tsx
│   │   │   ├── MarkdownEditor.tsx
│   │   │   ├── MarkdownPreview.tsx
│   │   │   └── SyncManager.tsx
│   │   ├── upload/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── DragDropZone.tsx
│   │   │   └── ProgressIndicator.tsx
│   │   ├── history/
│   │   │   ├── HistoryPanel.tsx
│   │   │   └── HistoryItem.tsx
│   │   ├── search/
│   │   │   ├── SearchBar.tsx
│   │   │   └── SearchResults.tsx
│   │   └── export/
│   │       ├── ExportButton.tsx
│   │       └── ExportModal.tsx
│   ├── lib/
│   │   ├── utils.ts
│   │   ├── constants.ts
│   │   ├── api.ts
│   │   ├── storage.ts
│   │   ├── parsers/
│   │   │   ├── pdf-parser.ts
│   │   │   ├── docx-parser.ts
│   │   │   ├── xlsx-parser.ts
│   │   │   ├── pptx-parser.ts
│   │   │   ├── txt-parser.ts
│   │   │   └── image-parser.ts
│   │   ├── processors/
│   │   │   ├── markdown-converter.ts
│   │   │   ├── table-extractor.ts
│   │   │   ├── math-converter.ts
│   │   │   └── image-analyzer.ts
│   │   └── validators/
│   │       ├── file-validator.ts
│   │       └── content-validator.ts
│   ├── types/
│   │   ├── document.ts
│   │   ├── api.ts
│   │   ├── parser.ts
│   │   └── ui.ts
│   ├── hooks/
│   │   ├── useFileUpload.ts
│   │   ├── useDocumentProcessor.ts
│   │   ├── useMarkdownEditor.ts
│   │   ├── useHistory.ts
│   │   ├── useSearch.ts
│   │   └── useKeyboardShortcuts.ts
│   ├── context/
│   │   ├── DocumentContext.tsx
│   │   ├── HistoryContext.tsx
│   │   └── UIContext.tsx
│   └── styles/
│       ├── globals.css
│       ├── components.css
│       └── themes.css
├── python-processor/
│   ├── requirements.txt
│   ├── main.py
│   ├── app.py
│   ├── config.py
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── xlsx_parser.py
│   │   ├── pptx_parser.py
│   │   ├── txt_parser.py
│   │   └── image_parser.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── markdown_converter.py
│   │   ├── table_extractor.py
│   │   ├── math_converter.py
│   │   └── image_analyzer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── openai_client.py
│   │   └── validation.py
│   └── tests/
│       ├── __init__.py
│       ├── test_parsers.py
│       ├── test_processors.py
│       └── test_utils.py
├── docs/
│   ├── api-documentation.md
│   ├── deployment-guide.md
│   ├── user-manual.md
│   └── troubleshooting.md
└── tests/
    ├── __tests__/
    │   ├── components/
    │   ├── pages/
    │   ├── api/
    │   └── utils/
    ├── e2e/
    │   ├── upload.spec.ts
    │   ├── processing.spec.ts
    │   └── export.spec.ts
    └── fixtures/
        ├── sample.pdf
        ├── sample.docx
        ├── sample.xlsx
        ├── sample.pptx
        ├── sample.txt
        └── sample.png
```

## 2. Core Implementation Examples

### 2.1. File Upload Component

```typescript
// src/components/upload/FileUpload.tsx
'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { toast } from '@/components/ui/toast';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
  progress: number;
}

const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'text/plain': ['.txt'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  isProcessing,
  progress,
}) => {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      if (rejectedFiles.length > 0) {
        const error = rejectedFiles[0].errors[0];
        if (error.code === 'file-too-large') {
          toast.error('File size must be less than 50MB');
        } else if (error.code === 'file-invalid-type') {
          toast.error('Unsupported file type. Please upload PDF, DOCX, XLSX, PPTX, TXT, PNG, or JPG files.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    disabled: isProcessing,
  });

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-950' 
            : 'border-gray-300 hover:border-gray-400 dark:border-gray-600 dark:hover:border-gray-500'
          }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {isProcessing ? (
            <>
              <FileText className="w-12 h-12 text-blue-500 animate-pulse" />
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
                  Processing your document...
                </p>
                <Progress value={progress} className="w-64" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {progress}% complete
                </p>
              </div>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400" />
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop your document here'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  or click to browse files
                </p>
              </div>
              <Button variant="outline" className="mt-4">
                Choose File
              </Button>
              <div className="flex flex-wrap gap-2 mt-4">
                {['PDF', 'DOCX', 'XLSX', 'PPTX', 'TXT', 'PNG', 'JPG'].map((type) => (
                  <span
                    key={type}
                    className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-800 rounded"
                  >
                    {type}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
```

### 2.2. Document Viewer Component

```typescript
// src/components/document/DocumentViewer.tsx
'use client';

import React, { useEffect, useRef, useState } from 'react';
import { ZoomIn, ZoomOut, RotateCw, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DocumentViewerProps {
  file: File | null;
  documentUrl?: string;
  onSectionClick?: (sectionId: string) => void;
  highlightedSection?: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  file,
  documentUrl,
  onSectionClick,
  highlightedSection,
}) => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 50));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleDownload = () => {
    if (file) {
      const url = URL.createObjectURL(file);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const renderDocument = () => {
    if (!file && !documentUrl) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
          <div className="text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg">No document selected</p>
            <p className="text-sm">Upload a file to view it here</p>
          </div>
        </div>
      );
    }

    if (file?.type === 'application/pdf' || documentUrl?.endsWith('.pdf')) {
      return (
        <iframe
          src={documentUrl || URL.createObjectURL(file!)}
          className="w-full h-full border-0"
          style={{
            transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
            transformOrigin: 'top left',
          }}
          title="PDF Viewer"
        />
      );
    }

    if (file?.type.startsWith('image/')) {
      return (
        <div className="flex items-center justify-center h-full">
          <img
            src={URL.createObjectURL(file)}
            alt="Document preview"
            className="max-w-full max-h-full object-contain"
            style={{
              transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
            }}
          />
        </div>
      );
    }

    // For other document types, show a placeholder or use a document preview service
    return (
      <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
        <div className="text-center">
          <FileText className="w-16 h-16 mx-auto mb-4" />
          <p className="text-lg">{file?.name}</p>
          <p className="text-sm">Document preview not available</p>
          <p className="text-xs mt-2">Processing will extract content for markdown conversion</p>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleZoomOut}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <span className="text-sm font-medium min-w-[60px] text-center">
            {zoom}%
          </span>
          <Button variant="outline" size="sm" onClick={handleZoomIn}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleRotate}>
            <RotateCw className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="flex items-center space-x-2">
          {file && (
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="w-4 h-4 mr-1" />
              Download
            </Button>
          )}
        </div>
      </div>

      {/* Document Content */}
      <div ref={viewerRef} className="flex-1 overflow-auto">
        {renderDocument()}
      </div>
    </div>
  );
};
```

### 2.3. Markdown Editor Component

```typescript
// src/components/document/MarkdownEditor.tsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Eye, Edit, Copy, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/toast';

interface MarkdownEditorProps {
  content: string;
  onChange: (content: string) => void;
  onSectionClick?: (sectionId: string) => void;
  highlightedSection?: string;
  isPreviewMode?: boolean;
  onTogglePreview?: () => void;
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  content,
  onChange,
  onSectionClick,
  highlightedSection,
  isPreviewMode = false,
  onTogglePreview,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Auto-save functionality
  useEffect(() => {
    const timer = setTimeout(() => {
      if (content) {
        localStorage.setItem('markdown-draft', content);
        setLastSaved(new Date());
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [content]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 's':
            e.preventDefault();
            handleSave();
            break;
          case 'p':
            e.preventDefault();
            onTogglePreview?.();
            break;
          case 'c':
            if (e.shiftKey) {
              e.preventDefault();
              handleCopy();
            }
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [content]);

  const handleSave = () => {
    localStorage.setItem('markdown-content', content);
    setLastSaved(new Date());
    toast.success('Content saved successfully');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    toast.success('Content copied to clipboard');
  };

  const renderMarkdown = (markdown: string) => {
    // Simple markdown rendering - in production, use a library like react-markdown
    return markdown
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/\n/gim, '<br>');
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Button
            variant={isPreviewMode ? "outline" : "default"}
            size="sm"
            onClick={onTogglePreview}
          >
            {isPreviewMode ? (
              <>
                <Edit className="w-4 h-4 mr-1" />
                Edit
              </>
            ) : (
              <>
                <Eye className="w-4 h-4 mr-1" />
                Preview
              </>
            )}
          </Button>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="w-4 h-4 mr-1" />
            Copy
          </Button>
          <Button variant="outline" size="sm" onClick={handleSave}>
            <Save className="w-4 h-4 mr-1" />
            Save
          </Button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {isPreviewMode ? (
          <div
            ref={previewRef}
            className="h-full overflow-auto p-4 prose prose-sm max-w-none dark:prose-invert"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
          />
        ) : (
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => onChange(e.target.value)}
            className="w-full h-full p-4 border-0 resize-none focus:outline-none bg-transparent font-mono text-sm"
            placeholder="Your markdown content will appear here..."
            spellCheck={false}
          />
        )}
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between p-2 text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <span>{content.length} characters</span>
          <span>{content.split('\n').length} lines</span>
          <span>{content.split(/\s+/).filter(word => word.length > 0).length} words</span>
        </div>
        
        {lastSaved && (
          <span>
            Last saved: {lastSaved.toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};
```

### 2.4. Document Processing Hook

```typescript
// src/hooks/useDocumentProcessor.ts
'use client';

import { useState, useCallback } from 'react';
import { toast } from '@/components/ui/toast';

interface ProcessingResult {
  markdown: string;
  json: any;
  metadata: {
    fileName: string;
    fileType: string;
    fileSize: number;
    processedAt: Date;
    processingTime: number;
  };
}

interface ProcessingState {
  isProcessing: boolean;
  progress: number;
  result: ProcessingResult | null;
  error: string | null;
}

export const useDocumentProcessor = () => {
  const [state, setState] = useState<ProcessingState>({
    isProcessing: false,
    progress: 0,
    result: null,
    error: null,
  });

  const processDocument = useCallback(async (file: File) => {
    setState(prev => ({
      ...prev,
      isProcessing: true,
      progress: 0,
      error: null,
    }));

    const startTime = Date.now();

    try {
      // Step 1: Upload file
      setState(prev => ({ ...prev, progress: 10 }));
      
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file');
      }

      const { fileId } = await uploadResponse.json();
      setState(prev => ({ ...prev, progress: 30 }));

      // Step 2: Process document
      const processResponse = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fileId }),
      });

      if (!processResponse.ok) {
        throw new Error('Failed to process document');
      }

      setState(prev => ({ ...prev, progress: 70 }));

      const result = await processResponse.json();
      setState(prev => ({ ...prev, progress: 90 }));

      // Step 3: Finalize
      const processingTime = Date.now() - startTime;
      const finalResult: ProcessingResult = {
        ...result,
        metadata: {
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size,
          processedAt: new Date(),
          processingTime,
        },
      };

      setState(prev => ({
        ...prev,
        isProcessing: false,
        progress: 100,
        result: finalResult,
      }));

      // Save to history
      const history = JSON.parse(localStorage.getItem('document-history') || '[]');
      history.unshift(finalResult);
      localStorage.setItem('document-history', JSON.stringify(history.slice(0, 50))); // Keep last 50

      toast.success(`Document processed successfully in ${(processingTime / 1000).toFixed(1)}s`);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: errorMessage,
      }));
      toast.error(`Processing failed: ${errorMessage}`);
    }
  }, []);

  const clearResult = useCallback(() => {
    setState(prev => ({
      ...prev,
      result: null,
      error: null,
      progress: 0,
    }));
  }, []);

  return {
    ...state,
    processDocument,
    clearResult,
  };
};
```

### 2.5. API Route Example

```typescript
// src/app/api/process/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { writeFile, readFile, unlink } from 'fs/promises';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request: NextRequest) {
  try {
    const { fileId } = await request.json();

    if (!fileId) {
      return NextResponse.json(
        { error: 'File ID is required' },
        { status: 400 }
      );
    }

    // Read the uploaded file
    const tempDir = join(process.cwd(), 'temp');
    const filePath = join(tempDir, fileId);
    
    const fileBuffer = await readFile(filePath);
    
    // Send to Python processor
    const processorResponse = await fetch('http://localhost:8000/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
        'X-File-Name': fileId,
      },
      body: fileBuffer,
    });

    if (!processorResponse.ok) {
      throw new Error('Document processing failed');
    }

    const result = await processorResponse.json();

    // Clean up temp file
    await unlink(filePath);

    return NextResponse.json({
      markdown: result.markdown,
      json: result.json,
      sections: result.sections,
      images: result.images,
      tables: result.tables,
      math: result.math,
    });

  } catch (error) {
    console.error('Processing error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### 2.6. Python Document Processor

```python
# python-processor/app.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import os
from typing import Dict, Any

from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DOCXParser
from parsers.xlsx_parser import XLSXParser
from parsers.pptx_parser import PPTXParser
from parsers.txt_parser import TXTParser
from parsers.image_parser import ImageParser
from processors.markdown_converter import MarkdownConverter
from utils.openai_client import OpenAIClient

app = FastAPI(title="Document Parser API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers
parsers = {
    'application/pdf': PDFParser(),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DOCXParser(),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': XLSXParser(),
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': PPTXParser(),
    'text/plain': TXTParser(),
    'image/png': ImageParser(),
    'image/jpeg': ImageParser(),
}

markdown_converter = MarkdownConverter()
openai_client = OpenAIClient()

@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Process uploaded document and convert to markdown."""
    
    if not file.content_type or file.content_type not in parsers:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Parse document
        parser = parsers[file.content_type]
        parsed_data = parser.parse(temp_file_path)
        
        # Process images with OpenAI Vision if present
        if parsed_data.get('images'):
            for image in parsed_data['images']:
                description = await openai_client.describe_image(image['data'])
                image['description'] = description
        
        # Convert to markdown
        markdown_result = markdown_converter.convert(parsed_data)
        
        # Clean up
        os.unlink(temp_file_path)
        
        return {
            'markdown': markdown_result['markdown'],
            'json': parsed_data,
            'sections': markdown_result['sections'],
            'images': parsed_data.get('images', []),
            'tables': parsed_data.get('tables', []),
            'math': parsed_data.get('math', []),
            'metadata': {
                'file_name': file.filename,
                'file_type': file.content_type,
                'file_size': len(content),
            }
        }
        
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2.7. PDF Parser Implementation

```python
# python-processor/parsers/pdf_parser.py
import fitz  # PyMuPDF
import re
from typing import Dict, List, Any
from PIL import Image
import io
import base64

class PDFParser:
    """Parser for PDF documents using PyMuPDF."""
    
    def __init__(self):
        self.math_patterns = [
            r'\$[^$]+\$',  # Inline math
            r'\$\$[^$]+\$\$',  # Display math
            r'\\begin\{equation\}.*?\\end\{equation\}',  # LaTeX equations
            r'\\begin\{align\}.*?\\end\{align\}',  # LaTeX align
        ]
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF file and extract content."""
        doc = fitz.open(file_path)
        
        result = {
            'text': '',
            'images': [],
            'tables': [],
            'math': [],
            'metadata': {
                'pages': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
            }
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            result['text'] += f"\n\n--- Page {page_num + 1} ---\n\n{text}"
            
            # Extract images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    img_base64 = base64.b64encode(img_data).decode()
                    
                    result['images'].append({
                        'page': page_num + 1,
                        'index': img_index,
                        'data': img_base64,
                        'format': 'png',
                        'width': pix.width,
                        'height': pix.height,
                    })
                
                pix = None
            
            # Extract tables (basic implementation)
            tables = self._extract_tables(page)
            result['tables'].extend(tables)
            
            # Extract math expressions
            math_expressions = self._extract_math(text)
            result['math'].extend(math_expressions)
        
        doc.close()
        return result
    
    def _extract_tables(self, page) -> List[Dict[str, Any]]:
        """Extract tables from PDF page."""
        tables = []
        
        try:
            # Use PyMuPDF's table extraction
            tabs = page.find_tables()
            
            for tab_index, tab in enumerate(tabs):
                table_data = tab.extract()
                if table_data:
                    tables.append({
                        'data': table_data,
                        'bbox': tab.bbox,
                        'rows': len(table_data),
                        'cols': len(table_data[0]) if table_data else 0,
                    })
        
        except Exception as e:
            print(f"Table extraction error: {e}")
        
        return tables
    
    def _extract_math(self, text: str) -> List[Dict[str, Any]]:
        """Extract mathematical expressions from text."""
        math_expressions = []
        
        for pattern in self.math_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                math_expressions.append({
                    'expression': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'latex' if '\\' in match.group() else 'inline',
                })
        
        return math_expressions
```

## 3. Configuration Files

### 3.1. Package.json

```json
{
  "name": "document-parser-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "lucide-react": "^0.294.0",
    "react-dropzone": "^14.2.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "remark-math": "^6.0.0",
    "rehype-katex": "^7.0.0",
    "katex": "^0.16.0",
    "uuid": "^9.0.0",
    "@types/uuid": "^9.0.0",
    "clsx": "^2.0.0",
    "class-variance-authority": "^0.7.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.5.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^13.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest-environment-jsdom": "^29.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

### 3.2. Next.js Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/processor/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    return config;
  },
};

module.exports = nextConfig;
```

### 3.3. Python Requirements

```txt
# python-processor/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
PyMuPDF==1.23.8
python-docx==1.1.0
openpyxl==3.1.2
python-pptx==0.6.23
Pillow==10.1.0
openai==1.3.7
pydantic==2.5.0
python-dotenv==1.0.0
aiofiles==23.2.1
pandas==2.1.4
numpy==1.25.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

## 4. Deployment Instructions

### 4.1. Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd document-parser-app

# Install Node.js dependencies
npm install

# Set up Python environment
cd python-processor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your OpenAI API key and other configurations

# Start the Python processor
python app.py

# In another terminal, start the Next.js development server
cd ..
npm run dev
```

### 4.2. Production Deployment

```bash
# Build the Next.js application
npm run build

# Start the production server
npm start

# For Python processor, use a production ASGI server
cd python-processor
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

This comprehensive project structure and implementation examples provide a solid foundation for building the document parsing web application. The modular architecture allows for easy maintenance and extension, while the provided code examples demonstrate best practices for React/Next.js development and Python backend integration.

