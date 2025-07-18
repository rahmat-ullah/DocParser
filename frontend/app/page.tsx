import React, { useState, useEffect } from 'react';
import { Toaster } from '@/components/ui/toaster';
import { QueryProvider } from '@/providers/QueryProvider';
import FileUpload from '@/components/FileUpload';
import DocumentHistory from '@/components/DocumentHistory';
import DocumentViewer from '@/components/DocumentViewer';
import MarkdownEditor from '@/components/MarkdownEditor';
import ProcessingIndicator from '@/components/ProcessingIndicator';
import { useUploadStore } from '@/hooks/useUploadStore';
import { useSocketProgress } from '@/hooks/useSocketProgress';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { FileText, History, Settings, Menu, X } from 'lucide-react';

function AppContent() {
  const { 
    selectedDocument, 
    isProcessing, 
    processingStage, 
    processingProgress,
    error,
    setError 
  } = useUploadStore();

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  useSocketProgress();

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Modern Header */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden"
            >
              {isSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
            <div className="flex items-center gap-2">
              <FileText className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-semibold text-foreground">Document Parser</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="hidden sm:flex">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal" className="h-full">
          {/* Sidebar */}
          {(isSidebarOpen || !isMobile) && (
            <>
              <ResizablePanel 
                defaultSize={20} 
                minSize={15} 
                maxSize={30}
                className={`${isMobile ? 'absolute inset-y-0 left-0 z-50 bg-card shadow-lg' : ''}`}
              >
                <div className="h-full flex flex-col bg-card border-r border-border">
                  <div className="p-4 border-b border-border">
                    <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                      <History className="h-4 w-4" />
                      Recent Documents
                    </div>
                  </div>
                  <div className="flex-1 overflow-auto">
                    <DocumentHistory />
                  </div>
                </div>
              </ResizablePanel>
              {!isMobile && <ResizableHandle className="w-1 bg-border hover:bg-primary/20 transition-colors" />}
            </>
          )}

          {/* Main Content Area */}
          <ResizablePanel defaultSize={80} minSize={50}>
            {!selectedDocument ? (
              /* Welcome Screen */
              <div className="h-full flex items-center justify-center p-8">
                <div className="max-w-2xl w-full text-center space-y-8">
                  <div className="space-y-4">
                    <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                      <FileText className="h-8 w-8 text-primary" />
                    </div>
                    <h2 className="text-3xl font-bold text-foreground">
                      Welcome to Document Parser
                    </h2>
                    <p className="text-lg text-muted-foreground max-w-md mx-auto">
                      Upload your documents and convert them to markdown with AI-powered parsing
                    </p>
                  </div>

                  <div className="bg-card rounded-xl border border-border shadow-sm p-8">
                    <FileUpload />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <div className="font-medium text-foreground mb-1">Supported Formats</div>
                      <div className="text-muted-foreground">PDF, DOCX, XLSX, PPTX, TXT, Images</div>
                    </div>
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <div className="font-medium text-foreground mb-1">AI-Powered</div>
                      <div className="text-muted-foreground">Advanced parsing with context understanding</div>
                    </div>
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <div className="font-medium text-foreground mb-1">Export Ready</div>
                      <div className="text-muted-foreground">Clean markdown output for any platform</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              /* Document View */
              <ResizablePanelGroup direction="horizontal" className="h-full">
                <ResizablePanel defaultSize={50} minSize={30}>
                  <div className="h-full bg-background border-r border-border">
                    <div className="p-4 border-b border-border bg-card">
                      <h3 className="font-medium text-foreground">Original Document</h3>
                    </div>
                    <div className="h-[calc(100%-4rem)] overflow-auto">
                      <DocumentViewer />
                    </div>
                  </div>
                </ResizablePanel>

                <ResizableHandle className="w-1 bg-border hover:bg-primary/20 transition-colors" />

                <ResizablePanel defaultSize={50} minSize={30}>
                  <div className="h-full bg-background">
                    <div className="p-4 border-b border-border bg-card">
                      <h3 className="font-medium text-foreground">Markdown Output</h3>
                    </div>
                    <div className="h-[calc(100%-4rem)] overflow-auto">
                      <MarkdownEditor />
                    </div>
                  </div>
                </ResizablePanel>
              </ResizablePanelGroup>
            )}
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      {/* Processing Overlay */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg shadow-xl p-6 m-4 max-w-md w-full">
            <ProcessingIndicator />
          </div>
        </div>
      )}

      {/* Mobile Sidebar Overlay */}
      {isMobile && isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <Toaster />
    </div>
  );
}

export default function Home() {
  return (
    <QueryProvider>
      <AppContent />
    </QueryProvider>
  );
}