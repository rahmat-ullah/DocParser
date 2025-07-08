'use client';

import { useEffect } from 'react';
import { FileText, ChevronLeft, ChevronRight, Settings, HelpCircle, Menu } from 'lucide-react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { ParsedDocument, DocumentSection } from '@/types/document';
import { useUploadStore } from '@/hooks/useUploadStore';
import { useDocumentHistoryQuery, useUpdateDocumentMutation } from '@/hooks/useDocumentQuery';
import { DocumentParser } from '@/lib/documentParser';
import { DocumentHistoryManager } from '@/lib/documentHistory';
import { FileUpload } from '@/components/FileUpload';
import { DocumentViewer } from '@/components/DocumentViewer';
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
  }, []);

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    setProcessingProgress({
      stage: 'uploading',
      progress: 0,
      message: 'Preparing file for processing...'
    });

    try {
      const parser = DocumentParser.getInstance();
      const document = await parser.parseDocument(file, (progress, message) => {
        setProcessingProgress(prev => ({
          ...prev,
          progress,
          message,
          stage: progress < 30 ? 'uploading' : 
                progress < 70 ? 'parsing' : 
                progress < 90 ? 'converting' : 'complete'
        }));
      });

      setCurrentDocument(document);
      setSelectedSection(document.sections[0] || null);

      // Add to history
      const historyManager = DocumentHistoryManager.getInstance();
      historyManager.addDocument(document);
      
      setProcessingProgress({
        stage: 'complete',
        progress: 100,
        message: 'Document processed successfully!'
      });
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
      setCurrentDocument({
        ...currentDocument,
        markdownContent: markdown
      });
    }
  };

  const handleDocumentSelect = (document: ParsedDocument) =\u003e {
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
    <div className="min-h-screen bg-secondary flex flex-col">
      {/* Header */}
      <header className="bg-secondary border-b border-border px-4 md:px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <FileText className="w-6 h-6 md:w-8 md:h-8 text-primary" />
              <h1 className="text-xl md:text-2xl font-bold text-foreground">DocParser</h1>
            </div>
            <div className="hidden md:block text-sm text-muted-foreground ml-4">
              Convert documents to markdown with ease
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
onClick={() =\u003e toggleHistory()}
              variant={showHistory ? 'default' : 'ghost'}
              aria-label="Toggle history sidebar"
            />
            <IconButton
              icon={<Settings className="w-5 h-5" />}
              onClick={() =\u003e toggleSettings()}
              variant="ghost"
              aria-label="Settings"
            />
            <IconButton
              icon={<HelpCircle className="w-5 h-5" />}
              variant="ghost"
              aria-label="Help"
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <PanelGroup direction="horizontal" className="flex-1">
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
                <DocumentHistory
                  onDocumentSelect={handleDocumentSelect}
                  selectedDocument={currentDocument}
                  className="h-full"
                />
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

          {/* Main Content Area */}
          {!showHistory || !isMobile ? (
            <Panel defaultSize={showHistory ? 75 : 100} minSize={30}>
              {/* Upload Area */}
              {!currentDocument && !isProcessing && (
                <div className="flex-1 flex items-center justify-center p-4 md:p-8">
                  <div className="max-w-2xl w-full">
                    <div className="text-center mb-8">
                      <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
                        Transform Documents into Markdown
                      </h2>
                      <p className="text-base md:text-lg text-muted-foreground mb-8">
                        Upload your documents and convert them to clean, structured markdown format
                      </p>
                    </div>
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      isProcessing={isProcessing}
                    />
                  </div>
                </div>
              )}

              {/* Processing Indicator */}
              {isProcessing && (
                <div className="flex-1 flex items-center justify-center p-4 md:p-8">
                  <div className="max-w-md w-full">
                    <ProcessingIndicator progress={processingProgress} />
                  </div>
                </div>
              )}

              {/* Document Processing View */}
              {currentDocument && !isProcessing && (
                <PanelGroup direction={isMobile ? "vertical" : "horizontal"} className="h-full">
                  {/* Document Viewer */}
                  <Panel defaultSize={50} minSize={30}>
                    <DocumentViewer
                      document={currentDocument}
                      selectedSection={selectedSection}
                      onSectionSelect={handleSectionSelect}
                      className="h-full"
                    />
                  </Panel>

                  {/* Resizable Handle */}
                  <PanelResizeHandle 
                    className={cn(
                      "bg-border hover:bg-muted transition-colors",
                      isMobile ? "h-2 cursor-row-resize" : "w-2 cursor-col-resize"
                    )}
                  />

                  {/* Markdown Editor */}
                  <Panel defaultSize={50} minSize={30}>
                    <MarkdownEditor
                      document={currentDocument}
                      selectedSection={selectedSection}
                      onMarkdownChange={handleMarkdownChange}
                      onSectionSelect={handleSectionSelect}
                      className="h-full"
                    />
                  </Panel>
                </PanelGroup>
              )}
            </Panel>
          ) : null}
        </PanelGroup>
      </div>

      {/* Footer */}
      <footer className="bg-background border-t border-border px-4 md:px-6 py-3 flex-shrink-0">
        <div className="flex flex-col md:flex-row items-center justify-between text-sm text-muted-foreground space-y-2 md:space-y-0">
          <div className="flex items-center space-x-4">
            <span>DocParser v1.0</span>
            <span className="hidden md:inline">•</span>
            <span>
              {currentDocument ? `${currentDocument.sections.length} sections` : 'No document loaded'}
            </span>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <span>Shortcuts: Ctrl+H (History), Ctrl+S (Save), Ctrl+, (Settings)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}