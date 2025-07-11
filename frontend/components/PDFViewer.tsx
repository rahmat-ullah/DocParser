'use client';

import { useState, useEffect } from 'react';
import { FileText, Download, AlertCircle, Loader2, ExternalLink } from 'lucide-react';
import { ParsedDocument } from '@/types/document';
import { cn } from '@/lib/utils';
import { Panel } from '@/components/ui/panel';
import { IconButton } from '@/components/ui/icon-button';

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

  const handleDownload = () => {
    if (document) {
      const pdfUrl = `${API_BASE_URL}/documents/${document.id}/file`;
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = document.metadata.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleOpenExternal = () => {
    if (document) {
      const pdfUrl = `${API_BASE_URL}/documents/${document.id}/file`;
      window.open(pdfUrl, '_blank');
    }
  };

  if (!document) {
    return (
      <Panel className={cn('flex flex-col h-full', className)} variant="ghost" padding="none">
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg mb-2">No document selected</p>
            <p className="text-sm">Upload a document to view its PDF</p>
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
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center space-x-2 min-w-0">
          <FileText className="w-5 h-5 text-primary flex-shrink-0" />
          <h2 className="text-lg font-semibold text-foreground truncate">
            {document.metadata.name}
          </h2>
        </div>
        
        <div className="flex items-center space-x-2">
          <IconButton
            icon={<ExternalLink className="w-4 h-4" />}
            onClick={handleOpenExternal}
            variant="ghost"
            aria-label="Open in new tab"
            title="Open in new tab"
          />
          <IconButton
            icon={<Download className="w-4 h-4" />}
            onClick={handleDownload}
            variant="ghost"
            aria-label="Download PDF"
            title="Download PDF"
          />
        </div>
      </div>

      {/* PDF Content */}
      <div className="flex-1 relative bg-muted/50">
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
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-destructive" />
              <p className="text-lg font-medium text-foreground mb-2">Unable to display PDF inline</p>
              <p className="text-sm text-muted-foreground mb-4">
                Your browser may not support inline PDF viewing. You can open or download the file instead.
              </p>
              <div className="space-y-2">
                <button
                  onClick={handleOpenExternal}
                  className="block w-full px-4 py-2 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
                >
                  Open PDF in new tab
                </button>
                <button
                  onClick={handleDownload}
                  className="block w-full px-4 py-2 text-sm border border-border rounded hover:bg-accent transition-colors"
                >
                  Download PDF
                </button>
              </div>
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
