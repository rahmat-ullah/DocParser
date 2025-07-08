'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, ZoomIn, ZoomOut, RotateCw, X } from 'lucide-react';
import { ParsedDocument, DocumentSection } from '@/types/document';
import { cn } from '@/lib/utils';

interface DocumentViewerProps {
  document: ParsedDocument | null;
  selectedSection: DocumentSection | null;
  onSectionSelect: (section: DocumentSection) => void;
  className?: string;
}

export function DocumentViewer({ 
  document, 
  selectedSection, 
  onSectionSelect,
  className 
}: DocumentViewerProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [zoom, setZoom] = useState(100);
  const [highlightedText, setHighlightedText] = useState<string>('');
  const [showSearch, setShowSearch] = useState(false);
  const viewerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selectedSection && viewerRef.current) {
      // Scroll to the selected section
      const element = viewerRef.current.querySelector(`[data-section-id="${selectedSection.id}"]`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [selectedSection]);

  const highlightText = (text: string, term: string): string => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>');
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setHighlightedText(term);
  };

  const clearSearch = () => {
    setSearchTerm('');
    setHighlightedText('');
    setShowSearch(false);
  };

  const renderContent = () => {
    if (!document) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No document selected</p>
            <p className="text-sm">Upload a document to get started</p>
          </div>
        </div>
      );
    }

    return (
      <div 
        ref={viewerRef}
        className="prose prose-sm max-w-none p-4 md:p-6"
        style={{ zoom: `${zoom}%` }}
      >
        <div className="space-y-4">
          {document.sections.map((section) => (
            <div
              key={section.id}
              data-section-id={section.id}
              className={cn(
                'cursor-pointer p-3 rounded-lg border transition-all duration-200',
                selectedSection?.id === section.id 
                  ? 'border-primary bg-primary/10 shadow-sm' 
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              )}
              onClick={() => onSectionSelect(section)}
            >
              <h3 className="font-medium text-gray-900 mb-2 text-sm md:text-base">
                {section.title}
              </h3>
              <div 
                className="text-gray-700 text-xs md:text-sm leading-relaxed"
                dangerouslySetInnerHTML={{ 
                  __html: searchTerm ? highlightText(section.content, searchTerm) : section.content 
                }}
              />
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={cn('flex flex-col h-full bg-white border-r border-gray-200', className)}>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between p-4 border-b border-gray-200 space-y-3 md:space-y-0">
        <div className="flex items-center space-x-4 min-w-0">
          <h2 className="text-lg font-semibold text-gray-900 truncate">
            {document?.metadata.name || 'Document Viewer'}
          </h2>
          {document && (
            <span className="text-sm text-gray-500 flex-shrink-0">
              {document.sections.length} sections
            </span>
          )}
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSearch(!showSearch)}
            className={cn(
              'p-2 rounded-lg transition-colors',
              showSearch ? 'bg-primary text-white' : 'text-gray-600 hover:bg-gray-100'
            )}
            aria-label="Toggle search"
          >
            <Search className="w-4 h-4" />
          </button>
          
          {/* Zoom Controls */}
          <div className="flex items-center space-x-1 border border-gray-300 rounded-lg">
            <button
              onClick={() => setZoom(Math.max(50, zoom - 10))}
              className="p-2 hover:bg-gray-100 rounded-l-lg"
              aria-label="Zoom out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="px-2 py-1 text-sm font-medium border-x border-gray-300 min-w-[50px] text-center">
              {zoom}%
            </span>
            <button
              onClick={() => setZoom(Math.min(200, zoom + 10))}
              className="p-2 hover:bg-gray-100 rounded-r-lg"
              aria-label="Zoom in"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search in document..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              autoFocus
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
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
}