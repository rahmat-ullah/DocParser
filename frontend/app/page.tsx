'use client';

import { useEffect } from 'react';
import { FileText, ChevronLeft, ChevronRight, Settings, HelpCircle, Menu } from 'lucide-react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { ParsedDocument, DocumentSection } from '@/types/document';
import { useUploadStore } from '@/hooks/useUploadStore';
import { useDocumentHistoryQuery, useUpdateDocumentMutation } from '@/hooks/useDocumentQuery';
import { uploadDocument, processDocument, getProcessingStatus, getProcessingResult } from '@/lib/documentApi';
import { DocumentHistoryManager } from '@/lib/documentHistory';
import { FileUpload } from '@/components/FileUpload';
import { PDFViewer } from '@/components/PDFViewer';
import { MarkdownEditor } from '@/components/MarkdownEditor';
import { DocumentHistory } from '@/components/DocumentHistory';
import { ProcessingIndicator } from '@/components/ProcessingIndicator';
import { DocumentSuspense } from '@/components/DocumentSuspense';
import { IconButton } from '@/components/ui/icon-button';
import { cn } from '@/lib/utils';

export default function Home() {
  // Zustand store for UI state management
  const {
    currentDocument,
    selectedSection,
    isProcessing,
    processingProgress,
    showHistory,
    showSettings,
    isMobile,
    setCurrentDocument,
    setSelectedSection,
    setIsProcessing,
    setProcessingProgress,
    setShowHistory,
    setIsMobile,
    toggleHistory,
    toggleSettings,
    selectDocumentWithSection
  } = useUploadStore();

  // React Query hooks for data management
  const { data: documentHistory, addDocumentToHistory } = useDocumentHistoryQuery();
  const updateDocumentMutation = useUpdateDocumentMutation();

  // Check for mobile viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setShowHistory(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [setIsMobile, setShowHistory]);

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    setProcessingProgress({
      stage: 'uploading',
      progress: 0,
      message: 'Uploading file...'
    });

    try {
      // Step 1: Upload file
      setProcessingProgress({
        stage: 'uploading',
        progress: 20,
        message: 'Uploading document to server...'
      });
      
      const uploadResult = await uploadDocument(file);
      const documentId = uploadResult.id;
      
      // Step 2: Start processing
      setProcessingProgress({
        stage: 'parsing',
        progress: 40,
        message: 'Processing document...'
      });
      
      await processDocument(documentId);
      
      // Step 3: Poll for processing status
      let processingComplete = false;
      let attempts = 0;
      const maxAttempts = 300; // 5 minutes timeout for table extraction
      
      while (!processingComplete && attempts < maxAttempts) {
        const status = await getProcessingStatus(documentId);
        
        if (status.status === 'completed') {
          processingComplete = true;
          setProcessingProgress({
            stage: 'converting',
            progress: 80,
            message: 'Retrieving results...'
          });
          
          // Get the final result
          const result = await getProcessingResult(documentId);
          
          // Create a ParsedDocument from the backend response
          const document: ParsedDocument = {
            id: documentId,
            metadata: {
              id: documentId,
              name: file.name,
              type: file.type,
              size: file.size,
              uploadDate: new Date(),
              lastModified: new Date(file.lastModified)
            },
            originalContent: result.extracted_text || '',
            markdownContent: result.extracted_text || '',
            markdownUrl: result.markdown_url,
            sections: []
          };
          
          selectDocumentWithSection(document);
          
          // Add to history
          const historyManager = DocumentHistoryManager.getInstance();
          historyManager.addDocument(document);
          if (documentHistory && !Array.isArray(documentHistory)) {
            // Initialize history if it's not an array
            addDocumentToHistory(document);
          } else {
            addDocumentToHistory(document);
          }
          
          setProcessingProgress({
            stage: 'complete',
            progress: 100,
            message: 'Document processed successfully!'
          });
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Processing failed');
        } else {
          // Still processing
          setProcessingProgress({
            stage: 'parsing',
            progress: Math.min(40 + (attempts * 0.5), 75),
            message: `Processing document... This may take a moment. (${attempts}s)`
          });
          
          // Wait 1 second before next check
          await new Promise(resolve => setTimeout(resolve, 1000));
          attempts++;
        }
      }
      
      if (!processingComplete) {
        throw new Error('Processing timeout');
      }
    } catch (error) {
      console.error('Failed to process document:', error);
      setProcessingProgress({
        stage: 'complete',
        progress: 0,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setTimeout(() => setIsProcessing(false), 1000);
    }
  };

  const handleMarkdownChange = (markdown: string) => {
    if (currentDocument) {
      // Use optimistic UI with React Query mutation
      updateDocumentMutation.mutate({
        fileId: currentDocument.id,
        updates: { markdownContent: markdown }
      });
      
      // Also update Zustand store immediately for UI responsiveness
      setCurrentDocument({
        ...currentDocument,
        markdownContent: markdown
      });
    }
  };

  const handleDocumentSelect = (document: ParsedDocument) => {
    selectDocumentWithSection(document);
  };

  const handleSectionSelect = (section: DocumentSection) => {
    setSelectedSection(section);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'h':
            e.preventDefault();
            toggleHistory();
            break;
          case 's':
            e.preventDefault();
            // Auto-save is handled automatically
            break;
          case ',':
            e.preventDefault();
            toggleSettings();
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleHistory, toggleSettings]);

  return (
    <div className="h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 px-4 md:px-6 py-4 flex-shrink-0 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  DocParser
                </h1>
                <div className="hidden md:block text-sm text-slate-600 dark:text-slate-400">
                  Transform documents into markdown
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <IconButton
              icon={isMobile ? (
                <Menu className="w-5 h-5" />
              ) : showHistory ? (
                <ChevronLeft className="w-5 h-5" />
              ) : (
                <ChevronRight className="w-5 h-5" />
              )}
              onClick={() => toggleHistory()}
              variant={showHistory ? 'default' : 'ghost'}
              aria-label="Toggle history sidebar"
              className="hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            />
            <IconButton
              icon={<Settings className="w-5 h-5" />}
              onClick={() => toggleSettings()}
              variant="ghost"
              aria-label="Settings"
              className="hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            />
            <IconButton
              icon={<HelpCircle className="w-5 h-5" />}
              variant="ghost"
              aria-label="Help"
              className="hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <PanelGroup direction="horizontal" className="flex-1 overflow-hidden">
          {/* History Sidebar */}
          {showHistory && (
            <>
              <Panel 
                defaultSize={isMobile ? 100 : 25} 
                minSize={isMobile ? 100 : 20}
                maxSize={isMobile ? 100 : 40}
                className={cn(
                  'transition-all duration-300 ease-in-out',
                  isMobile && 'absolute inset-0 z-50 bg-background'
                )}
              >
                <DocumentSuspense>
                  <DocumentHistory
                    onDocumentSelect={handleDocumentSelect}
                    selectedDocument={currentDocument}
                    className="h-full"
                  />
                </DocumentSuspense>
                {isMobile && (
                  <IconButton
                    icon={<ChevronLeft className="w-5 h-5" />}
                    onClick={() => setShowHistory(false)}
                    variant="secondary"
                    className="absolute top-4 right-4"
                    aria-label="Close history"
                  />
                )}
              </Panel>
              {!isMobile && (
                <PanelResizeHandle className="w-2 bg-border hover:bg-muted transition-colors cursor-col-resize" />
              )}
            </>
          )}

          {/* Upload/Processing Area - Only when no document */}
          {(!currentDocument && !isProcessing) && (
            <Panel defaultSize={showHistory ? 75 : 100} minSize={30}>
              <div className="flex-1 flex items-center justify-center p-4 md:p-8">
                <div className="max-w-2xl w-full">
                  <div className="text-center mb-8">
                    <div className="mb-6">
                      <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
                        <FileText className="w-10 h-10 text-white" />
                      </div>
                    </div>
                    <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-900 via-slate-700 to-slate-600 dark:from-slate-100 dark:via-slate-300 dark:to-slate-500 bg-clip-text text-transparent mb-4">
                      Transform Documents into Markdown
                    </h2>
                    <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
                      Upload your documents and convert them to clean, structured markdown format with AI-powered processing
                    </p>
                    <div className="flex flex-wrap justify-center gap-4 mb-8">
                      <div className="flex items-center space-x-2 bg-white dark:bg-slate-800 px-4 py-2 rounded-full shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-slate-700 dark:text-slate-300">AI-Powered</span>
                      </div>
                      <div className="flex items-center space-x-2 bg-white dark:bg-slate-800 px-4 py-2 rounded-full shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-slate-700 dark:text-slate-300">Multiple Formats</span>
                      </div>
                      <div className="flex items-center space-x-2 bg-white dark:bg-slate-800 px-4 py-2 rounded-full shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-slate-700 dark:text-slate-300">Real-time Preview</span>
                      </div>
                    </div>
                  </div>
                  <FileUpload
                    onFileSelect={handleFileSelect}
                    isProcessing={isProcessing}
                  />
                </div>
              </div>
            </Panel>
          )}

          {/* Processing Indicator */}
          {isProcessing && (
            <Panel defaultSize={showHistory ? 75 : 100} minSize={30}>
              <div className="flex-1 flex items-center justify-center p-4 md:p-8">
                <div className="max-w-md w-full">
                  <ProcessingIndicator progress={processingProgress} />
                </div>
              </div>
            </Panel>
          )}

          {/* PDF Viewer - Middle Panel */}
          {currentDocument && !isProcessing && !isMobile && (
            <>
              <Panel defaultSize={showHistory ? 37 : 50} minSize={25}>
                <DocumentSuspense>
                  <PDFViewer
                    document={currentDocument}
                    className="h-full"
                  />
                </DocumentSuspense>
              </Panel>

              {/* Resizable Handle */}
              <PanelResizeHandle 
                className="bg-border hover:bg-muted transition-colors w-2 cursor-col-resize"
                data-testid="split-pane-divider-pdf-markdown"
              />

              {/* Markdown Editor - Right Panel */}
              <Panel defaultSize={showHistory ? 38 : 50} minSize={25}>
                <DocumentSuspense>
                  <MarkdownEditor
                    document={currentDocument}
                    selectedSection={selectedSection}
                    onMarkdownChange={handleMarkdownChange}
                    onSectionSelect={handleSectionSelect}
                    className="h-full"
                  />
                </DocumentSuspense>
              </Panel>
            </>
          )}

          {/* Mobile: Show only one panel at a time */}
          {currentDocument && !isProcessing && isMobile && (
            <Panel defaultSize={100} minSize={100}>
              <DocumentSuspense>
                <MarkdownEditor
                  document={currentDocument}
                  selectedSection={selectedSection}
                  onMarkdownChange={handleMarkdownChange}
                  onSectionSelect={handleSectionSelect}
                  className="h-full"
                />
              </DocumentSuspense>
            </Panel>
          )}
        </PanelGroup>
      </div>

      {/* Footer */}
      <footer className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700 px-4 md:px-6 py-4 flex-shrink-0">
        <div className="flex flex-col md:flex-row items-center justify-between text-sm text-slate-600 dark:text-slate-400 space-y-2 md:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"></div>
              <span className="font-medium">DocParser v1.0</span>
            </div>
            <span className="hidden md:inline text-slate-400">•</span>
            <span>
              {currentDocument ? `${currentDocument.sections.length} sections processed` : 'Ready to process documents'}
            </span>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">
              <span>Shortcuts:</span>
              <span className="font-mono">Ctrl+H</span>
              <span className="font-mono">Ctrl+S</span>
              <span className="font-mono">Ctrl+,</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
