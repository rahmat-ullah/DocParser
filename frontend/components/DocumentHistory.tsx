'use client';

import { useState, useEffect } from 'react';
import { History, Search, Trash2, FileText, Calendar, HardDrive, X } from 'lucide-react';
import { ParsedDocument } from '@/types/document';
import { DocumentHistoryManager } from '@/lib/documentHistory';
import { cn } from '@/lib/utils';
import { Sidebar, SidebarHeader, SidebarTitle, SidebarContent, SidebarItem } from '@/components/ui/sidebar';
import { IconButton } from '@/components/ui/icon-button';

interface DocumentHistoryProps {
  onDocumentSelect: (document: ParsedDocument) => void;
  selectedDocument: ParsedDocument | null;
  className?: string;
}

export function DocumentHistory({ 
  onDocumentSelect, 
  selectedDocument, 
  className 
}: DocumentHistoryProps) {
  const [documents, setDocuments] = useState<ParsedDocument[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredDocuments, setFilteredDocuments] = useState<ParsedDocument[]>([]);

  useEffect(() => {
    const historyManager = DocumentHistoryManager.getInstance();
    const loadDocuments = () => {
      const docs = historyManager.getDocuments();
      setDocuments(docs);
      setFilteredDocuments(docs);
    };

    loadDocuments();
    // Set up a periodic refresh to catch changes from other components
    const interval = setInterval(loadDocuments, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const historyManager = DocumentHistoryManager.getInstance();
      const filtered = historyManager.searchDocuments(searchTerm);
      setFilteredDocuments(filtered);
    } else {
      setFilteredDocuments(documents);
    }
  }, [searchTerm, documents]);

  const handleRemoveDocument = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const historyManager = DocumentHistoryManager.getInstance();
    historyManager.removeDocument(id);
    setDocuments(prev => prev.filter(doc => doc.id !== id));
  };

  const handleClearHistory = () => {
    const historyManager = DocumentHistoryManager.getInstance();
    historyManager.clearHistory();
    setDocuments([]);
    setFilteredDocuments([]);
  };

  const clearSearch = () => {
    setSearchTerm('');
  };

  const formatDate = (date: Date | string): string => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string): React.ReactNode => {
    if (type.includes('pdf')) return <FileText className="w-4 h-4 text-red-500" />;
    if (type.includes('word') || type.includes('document')) return <FileText className="w-4 h-4 text-blue-500" />;
    if (type.includes('sheet') || type.includes('excel')) return <FileText className="w-4 h-4 text-green-500" />;
    if (type.includes('presentation')) return <FileText className="w-4 h-4 text-orange-500" />;
    if (type.includes('image')) return <FileText className="w-4 h-4 text-purple-500" />;
    return <FileText className="w-4 h-4 text-muted-foreground" />;
  };

  return (
    <Sidebar className={className}>
      <SidebarHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <History className="w-5 h-5 text-muted-foreground" />
            <SidebarTitle>History</SidebarTitle>
          </div>
          {documents.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="text-xs text-muted-foreground hover:text-destructive transition-colors"
            >
              Clear All
            </button>
          )}
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-10 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-ring focus:border-transparent text-sm"
          />
          {searchTerm && (
            <IconButton
              icon={<X className="w-4 h-4" />}
              onClick={clearSearch}
              variant="ghost"
              size="xs"
              className="absolute right-1 top-1/2 transform -translate-y-1/2"
              aria-label="Clear search"
            />
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        {filteredDocuments.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-4">
            <History className="w-12 h-12 mb-4 text-muted-foreground/50" />
            <p className="text-center">
              {searchTerm ? 'No documents found' : 'No documents yet'}
            </p>
            <p className="text-sm text-center mt-1">
              {searchTerm ? 'Try a different search term' : 'Upload a document to get started'}
            </p>
          </div>
        ) : (
          <div className="p-2">
            {filteredDocuments.map((document) => (
              <SidebarItem
                key={document.id}
                active={selectedDocument?.id === document.id}
                onClick={() => onDocumentSelect(document)}
                className="group flex items-start space-x-3 mb-2"
              >
                <div className="flex-shrink-0 mt-1">
                  {getFileIcon(document.metadata.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-foreground truncate text-sm">
                    {document.metadata.name}
                  </p>
                  <div className="flex flex-col space-y-1 mt-1">
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <Calendar className="w-3 h-3" />
                      <span>{formatDate(document.metadata.uploadDate)}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <HardDrive className="w-3 h-3" />
                      <span>{formatFileSize(document.metadata.size)}</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {document.sections.length} sections
                  </p>
                </div>
                
                <IconButton
                  icon={<Trash2 className="w-4 h-4" />}
                  onClick={(e) => handleRemoveDocument(document.id, e)}
                  variant="ghost"
                  size="xs"
                  className="opacity-0 group-hover:opacity-100 hover:text-destructive"
                  aria-label="Remove document"
                />
              </SidebarItem>
            ))}
          </div>
        )}
      </SidebarContent>
    </Sidebar>
  );
}