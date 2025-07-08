'use client';

import { useState, useEffect } from 'react';
import { FileText, ChevronLeft, ChevronRight, Settings, HelpCircle, Menu } from 'lucide-react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { ParsedDocument, DocumentSection, ParsingProgress } from '@/types/document';
import { DocumentParser } from '@/lib/documentParser';
import { DocumentHistoryManager } from '@/lib/documentHistory';
import { FileUpload } from '@/components/FileUpload';
import { DocumentViewer } from '@/components/DocumentViewer';
import { MarkdownEditor } from '@/components/MarkdownEditor';
import { DocumentHistory } from '@/components/DocumentHistory';
import { ProcessingIndicator } from '@/components/ProcessingIndicator';
import { cn } from '@/lib/utils';

export default function Home() {
  const [currentDocument, setCurrentDocument] = useState<ParsedDocument | null>(null);
  const [selectedSection, setSelectedSection] = useState<DocumentSection | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState<ParsingProgress>({
    stage: 'uploading',
    progress: 0,
    message: 'Initializing...'
  });
  const [showHistory, setShowHistory] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

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

  const handleDocumentSelect = (document: ParsedDocument) => {
    setCurrentDocument(document);
    setSelectedSection(document.sections[0] || null);
    if (isMobile) {
      setShowHistory(false);
    }
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
            setShowHistory(!showHistory);
            break;
          case 's':
            e.preventDefault();
            // Auto-save is handled automatically
            break;
          case ',':
            e.preventDefault();
            setShowSettings(!showSettings);
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showHistory, showSettings]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 md:px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <FileText className="w-6 h-6 md:w-8 md:h-8 text-primary" />
              <h1 className="text-xl md:text-2xl font-bold text-gray-900">DocParser</h1>
            </div>
            <div className="hidden md:block text-sm text-gray-500 ml-4">
              Convert documents to markdown with ease
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className={cn(
                'p-2 rounded-lg transition-colors',
                showHistory ? 'bg-primary text-white' : 'text-gray-600 hover:bg-gray-100'
              )}
              aria-label="Toggle history sidebar"
            >
              {isMobile ? (
                <Menu className="w-5 h-5" />
              ) : showHistory ? (
                <ChevronLeft className="w-5 h-5" />
              ) : (
                <ChevronRight className="w-5 h-5" />
              )}
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
            <button 
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
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
                  isMobile && 'absolute inset-0 z-50 bg-white'
                )}
              >
                <DocumentHistory
                  onDocumentSelect={handleDocumentSelect}
                  selectedDocument={currentDocument}
                  className="h-full"
                />
                {isMobile && (
                  <button
                    onClick={() => setShowHistory(false)}
                    className="absolute top-4 right-4 p-2 bg-gray-100 rounded-lg"
                    aria-label="Close history"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                )}
              </Panel>
              {!isMobile && (
                <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors cursor-col-resize" />
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
                      <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
                        Transform Documents into Markdown
                      </h2>
                      <p className="text-base md:text-lg text-gray-600 mb-8">
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
                      "bg-gray-200 hover:bg-gray-300 transition-colors",
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
      <footer className="bg-white border-t border-gray-200 px-4 md:px-6 py-3 flex-shrink-0">
        <div className="flex flex-col md:flex-row items-center justify-between text-sm text-gray-500 space-y-2 md:space-y-0">
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