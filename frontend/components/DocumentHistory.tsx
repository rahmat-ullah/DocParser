'use client';

import { useState, useEffect } from 'react';
import { History, Search, Trash2, FileText, Calendar, HardDrive, X } from 'lucide-react';
import { ParsedDocument } from '@/types/document';
import { DocumentHistoryManager } from '@/lib/documentHistory';
import { cn } from '@/lib/utils';

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
    return <FileText className="w-4 h-4 text-gray-500" />;
  };

  return (
    <div className={cn('flex flex-col h-full bg-white border-r border-gray-200', className)}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <History className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">History</h2>
          </div>
          {documents.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="text-xs text-gray-500 hover:text-red-500 transition-colors"
            >
              Clear All
            </button>
          )}
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
          />
          {searchTerm && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-auto">
        {filteredDocuments.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 p-4">
            <History className="w-12 h-12 mb-4 text-gray-300" />
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
              <div
                key={document.id}
                className={cn(
                  'group flex items-start space-x-3 p-3 rounded-lg cursor-pointer transition-all duration-200 mb-2',
                  selectedDocument?.id === document.id 
                    ? 'bg-primary/10 border border-primary/20' 
                    : 'hover:bg-gray-50 border border-transparent'
                )}
                onClick={() => onDocumentSelect(document)}
              >
                <div className="flex-shrink-0 mt-1">
                  {getFileIcon(document.metadata.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate text-sm">
                    {document.metadata.name}
                  </p>
                  <div className="flex flex-col space-y-1 mt-1">
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <Calendar className="w-3 h-3" />
                      <span>{formatDate(document.metadata.uploadDate)}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <HardDrive className="w-3 h-3" />
                      <span>{formatFileSize(document.metadata.size)}</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {document.sections.length} sections
                  </p>
                </div>
                
                <button
                  onClick={(e) => handleRemoveDocument(document.id, e)}
                  className="flex-shrink-0 p-1 hover:bg-gray-200 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                  aria-label="Remove document"
                >
                  <Trash2 className="w-4 h-4 text-gray-500 hover:text-red-500" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}