/**
 * PDF Compare Viewer Component
 * 
 * This component demonstrates how to implement the PDF viewer functionality
 * described in the instructions. It uses @react-pdf-viewer to display PDFs
 * inline without triggering browser downloads.
 */

import React, { useState, useEffect } from 'react';
import { Viewer, Worker } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { pageNavigationPlugin } from '@react-pdf-viewer/page-navigation';
import { zoomPlugin } from '@react-pdf-viewer/zoom';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

interface PdfCompareViewerProps {
  documentId: string;
  apiBaseUrl?: string;
}

interface PdfUrls {
  original: string;
  parsed: string;
  original_exists: boolean;
  parsed_exists: boolean;
  document_name: string;
  document_status: string;
}

const PdfCompareViewer: React.FC<PdfCompareViewerProps> = ({ 
  documentId, 
  apiBaseUrl = 'http://localhost:8000' 
}) => {
  const [pdfUrls, setPdfUrls] = useState<PdfUrls | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Create plugins with custom toolbar (removed download/print buttons)
  const pageNavigationPluginInstance = pageNavigationPlugin();
  const zoomPluginInstance = zoomPlugin();

  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    toolbarPlugin: {
      // Customize toolbar to hide download/print buttons
      renderDefaultToolbar: (Toolbar) => (
        <Toolbar>
          {(slots) => {
            const {
              CurrentPageInput,
              Download, // We'll hide this
              EnterFullScreen,
              GoToFirstPage,
              GoToLastPage,
              GoToNextPage,
              GoToPreviousPage,
              NumberOfPages,
              Print, // We'll hide this
              Zoom,
              ZoomIn,
              ZoomOut,
            } = slots;
            return (
              <div className="flex items-center space-x-2 p-2">
                <div className="flex items-center space-x-1">
                  <GoToFirstPage />
                  <GoToPreviousPage />
                  <CurrentPageInput />
                  <span className="text-sm">/ <NumberOfPages /></span>
                  <GoToNextPage />
                  <GoToLastPage />
                </div>
                <div className="flex items-center space-x-1">
                  <ZoomOut />
                  <Zoom />
                  <ZoomIn />
                </div>
                <EnterFullScreen />
                {/* Download and Print buttons are intentionally omitted */}
              </div>
            );
          }}
        </Toolbar>
      ),
    },
  });

  // Fetch PDF URLs when component mounts
  useEffect(() => {
    const fetchPdfUrls = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${apiBaseUrl}/api/v1/pdf/compare/${documentId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch PDF URLs: ${response.statusText}`);
        }
        
        const data = await response.json();
        setPdfUrls(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load PDF URLs');
      } finally {
        setLoading(false);
      }
    };

    fetchPdfUrls();
  }, [documentId, apiBaseUrl]);

  // Handle page change synchronization
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading PDF viewers...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">
          <p className="text-lg font-semibold">Error loading PDF</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!pdfUrls) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">
          <p className="text-lg font-semibold">No PDF data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-gray-100 p-4 border-b">
        <h2 className="text-xl font-semibold">PDF Comparison: {pdfUrls.document_name}</h2>
        <p className="text-sm text-gray-600">Status: {pdfUrls.document_status}</p>
      </div>

      {/* PDF Viewers */}
      <div className="flex-1 flex">
        {/* Original PDF */}
        <div className="flex-1 border-r">
          <div className="bg-gray-50 p-2 border-b">
            <h3 className="font-medium">Original PDF</h3>
            {!pdfUrls.original_exists && (
              <p className="text-sm text-yellow-600">Original file not found</p>
            )}
          </div>
          <div className="h-full overflow-auto">
            {pdfUrls.original_exists ? (
              <Worker workerUrl="https://unpkg.com/pdfjs-dist@latest/build/pdf.worker.min.js">
                <Viewer
                  fileUrl={pdfUrls.original}
                  plugins={[defaultLayoutPluginInstance]}
                  onPageChange={({ currentPage }) => handlePageChange(currentPage + 1)}
                  renderError={(error) => (
                    <div className="p-4 text-red-600">
                      <p>Error loading original PDF: {error.message}</p>
                    </div>
                  )}
                />
              </Worker>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Original PDF not available</p>
              </div>
            )}
          </div>
        </div>

        {/* Parsed PDF */}
        <div className="flex-1">
          <div className="bg-gray-50 p-2 border-b">
            <h3 className="font-medium">Parsed PDF</h3>
            {!pdfUrls.parsed_exists && (
              <p className="text-sm text-yellow-600">Parsed file not found - showing original</p>
            )}
          </div>
          <div className="h-full overflow-auto">
            <Worker workerUrl="https://unpkg.com/pdfjs-dist@latest/build/pdf.worker.min.js">
              <Viewer
                fileUrl={pdfUrls.parsed}
                plugins={[defaultLayoutPluginInstance]}
                onPageChange={({ currentPage }) => handlePageChange(currentPage + 1)}
                renderError={(error) => (
                  <div className="p-4 text-red-600">
                    <p>Error loading parsed PDF: {error.message}</p>
                  </div>
                )}
              />
            </Worker>
          </div>
        </div>
      </div>

      {/* Footer with sync controls */}
      <div className="bg-gray-100 p-2 border-t">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Current page: {currentPage}
          </div>
          <div className="text-sm text-gray-600">
            Use the toolbar controls to navigate and zoom
          </div>
        </div>
      </div>
    </div>
  );
};

export default PdfCompareViewer;

// Example usage:
// <PdfCompareViewer documentId="your-document-id" apiBaseUrl="http://localhost:8000" />
