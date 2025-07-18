'use client';

import { useState, useEffect } from 'react';
import { FileText, AlertCircle, Loader2 } from 'lucide-react';
import { ParsedDocument } from '@/types/document';
import { cn } from '@/lib/utils';
import { Panel } from '@/components/ui/panel';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

interface PDFViewerProps {
  document: ParsedDocument | null;
  className?: string;
}

export function PDFViewer({ document, className }: PDFViewerProps) {
  const [loading, setLoading] = useState(true);
  const [showInlineError, setShowInlineError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setShowInlineError(false);
  }, [document?.id]);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setLoading(false);
    setShowInlineError(true);
  };


  if (!document) {
    return (
      <Panel className={cn('flex flex-col h-full', className)} variant="ghost" padding="none">
        <div className="flex items-center justify-center h-full bg-slate-50 dark:bg-slate-800/50">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <p className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">No document selected</p>
            <p className="text-sm text-slate-600 dark:text-slate-400">Upload a document to view its PDF</p>
          </div>
        </div>
      </Panel>
    );
  }

  // Use relative URL to leverage Next.js proxy
  const pdfUrl = `/api/v1/documents/${document.id}/file`;

  return (
    <Panel 
      className={cn('flex flex-col h-full', className)} 
      variant="ghost" 
      padding="none"
      data-testid="pdf-viewer-pane"
    >
      {/* Header */}
      <div className="flex items-center p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-sm">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 truncate">
              {document.metadata.name}
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">PDF Document</p>
          </div>
        </div>
      </div>

      {/* PDF Content */}
      <div className="flex-1 relative bg-muted/50 overflow-auto">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
            <div className="flex flex-col items-center space-y-2">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Loading PDF...</p>
            </div>
          </div>
        )}

        {showInlineError ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center p-6">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
              <p className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">Unable to display PDF</p>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Your browser may not support inline PDF viewing. Please try refreshing the page or use a different browser.
              </p>
            </div>
          </div>
        ) : (
          <iframe
            src={pdfUrl}
            className="w-full h-full border-0"
            title={`PDF Viewer - ${document.metadata.name}`}
            onLoad={handleIframeLoad}
            onError={handleIframeError}
          />
        )}
      </div>
    </Panel>
  );
}
