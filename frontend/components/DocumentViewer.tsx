'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, ZoomIn, ZoomOut, RotateCw, X } from 'lucide-react';
import { ParsedDocument, DocumentSection } from '@/types/document';
import { cn } from '@/lib/utils';
import { Panel, PanelHeader, PanelContent } from '@/components/ui/panel';
import { IconButton } from '@/components/ui/icon-button';

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
        <div className="flex items-center justify-center h-full text-muted-foreground">
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
                  : 'border-border hover:border-border/80 hover:bg-accent/50'
              )}
              onClick={() => onSectionSelect(section)}
            >
              <h3 className="font-medium text-foreground mb-2 text-sm md:text-base">
                {section.title}
              </h3>
              <div 
                className="text-muted-foreground text-xs md:text-sm leading-relaxed"
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
    <Panel className={cn('flex flex-col h-full border-r', className)} variant="ghost" padding="none">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between p-4 border-b border-border space-y-3 md:space-y-0">
        <div className="flex items-center space-x-4 min-w-0">
          <h2 className="text-lg font-semibold text-foreground truncate">
            {document?.metadata.name || 'Document Viewer'}
          </h2>
          {document && (
            <span className="text-sm text-muted-foreground flex-shrink-0">
              {document.sections.length} sections
            </span>
          )}
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-2">
          <IconButton
            icon={<Search className="w-4 h-4" />}
            onClick={() => setShowSearch(!showSearch)}
            variant={showSearch ? 'default' : 'ghost'}
            aria-label="Toggle search"
          />
          
          {/* Zoom Controls */}
          <div className="flex items-center space-x-1 border border-border rounded-lg">
            <IconButton
              icon={<ZoomOut className="w-4 h-4" />}
              onClick={() => setZoom(Math.max(50, zoom - 10))}
              variant="ghost"
              className="rounded-r-none border-r border-border"
              aria-label="Zoom out"
            />
            <span className="px-2 py-1 text-sm font-medium text-foreground min-w-[50px] text-center">
              {zoom}%
            </span>
            <IconButton
              icon={<ZoomIn className="w-4 h-4" />}
              onClick={() => setZoom(Math.min(200, zoom + 10))}
              variant="ghost"
              className="rounded-l-none border-l border-border"
              aria-label="Zoom in"
            />
          </div>
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <div className="p-4 border-b border-border bg-muted/50">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search in document..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-10 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-ring focus:border-transparent"
              autoFocus
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
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </Panel>
  );
}