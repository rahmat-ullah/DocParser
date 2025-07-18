'use client';

import { useState, useEffect, useRef } from 'react';
import { Eye, Edit, Download, FileText, Copy, Check, Maximize2, Minimize2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { ParsedDocument, DocumentSection } from '@/types/document';
import { ExportManager } from '@/lib/exportUtils';
import { cn } from '@/lib/utils';

interface MarkdownEditorProps {
  document: ParsedDocument | null;
  selectedSection: DocumentSection | null;
  onMarkdownChange: (markdown: string) => void;
  onSectionSelect: (section: DocumentSection) => void;
  className?: string;
}

export function MarkdownEditor({ 
  document, 
  selectedSection, 
  onMarkdownChange,
  onSectionSelect,
  className 
}: MarkdownEditorProps) {
  const [isPreviewMode, setIsPreviewMode] = useState(true);
  const [markdownContent, setMarkdownContent] = useState('');
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (document) {
      setMarkdownContent(document.markdownContent);
    }
  }, [document]);

  useEffect(() => {
    if (selectedSection && previewRef.current) {
      const element = previewRef.current.querySelector(`[data-section="${selectedSection.id}"]`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [selectedSection]);

  const handleMarkdownChange = (value: string) => {
    setMarkdownContent(value);
    onMarkdownChange(value);
  };

  const handleCopy = async () => {
    if (markdownContent) {
      await navigator.clipboard.writeText(markdownContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExport = (format: 'markdown' | 'json') => {
    if (!document) return;
    
    if (format === 'markdown') {
      ExportManager.exportAsMarkdown(document);
    } else {
      ExportManager.exportAsJSON(document);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const renderPreview = () => {
    if (!document || !markdownContent) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No content to preview</p>
            <p className="text-sm">Start editing to see the preview</p>
          </div>
        </div>
      );
    }

    return (
      <div ref={previewRef} className="prose prose-sm max-w-none p-4 md:p-6">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            h1: ({ children, ...props }) => (
              <h1 {...props} className="text-xl md:text-2xl font-bold mb-4 text-gray-900">
                {children}
              </h1>
            ),
            h2: ({ children, ...props }) => (
              <h2 {...props} className="text-lg md:text-xl font-semibold mb-3 text-gray-900">
                {children}
              </h2>
            ),
            h3: ({ children, ...props }) => (
              <h3 {...props} className="text-base md:text-lg font-medium mb-2 text-gray-900">
                {children}
              </h3>
            ),
            p: ({ children, ...props }) => (
              <p {...props} className="mb-4 text-gray-700 leading-relaxed text-sm md:text-base">
                {children}
              </p>
            ),
            ul: ({ children, ...props }) => (
              <ul {...props} className="mb-4 ml-6 space-y-1">
                {children}
              </ul>
            ),
            ol: ({ children, ...props }) => (
              <ol {...props} className="mb-4 ml-6 space-y-1">
                {children}
              </ol>
            ),
            li: ({ children, ...props }) => (
              <li {...props} className="text-gray-700 text-sm md:text-base">
                {children}
              </li>
            ),
            code: ({ children, ...props }) => (
              <code {...props} className="bg-gray-100 px-2 py-1 rounded text-xs md:text-sm font-mono">
                {children}
              </code>
            ),
            pre: ({ children, ...props }) => (
              <pre {...props} className="bg-gray-100 p-4 rounded-lg overflow-x-auto mb-4 text-xs md:text-sm">
                {children}
              </pre>
            ),
            blockquote: ({ children, ...props }) => (
              <blockquote {...props} className="border-l-4 border-gray-300 pl-4 italic mb-4">
                {children}
              </blockquote>
            ),
            table: ({ children, ...props }) => (
              <div className="overflow-x-auto">
                <table {...props} className="w-full border-collapse border border-gray-300 mb-4 text-xs md:text-sm">
                  {children}
                </table>
              </div>
            ),
            th: ({ children, ...props }) => (
              <th {...props} className="border border-gray-300 px-2 md:px-4 py-2 bg-gray-50 font-medium">
                {children}
              </th>
            ),
            td: ({ children, ...props }) => (
              <td {...props} className="border border-gray-300 px-2 md:px-4 py-2">
                {children}
              </td>
            ),
          }}
        >
          {markdownContent}
        </ReactMarkdown>
      </div>
    );
  };

  const renderEditor = () => {
    return (
      <div className="h-full flex flex-col">
        <textarea
          ref={textareaRef}
          value={markdownContent}
          onChange={(e) => handleMarkdownChange(e.target.value)}
          className="flex-1 p-4 md:p-6 border-0 resize-none focus:outline-none font-mono text-xs md:text-sm leading-relaxed"
          placeholder="Start typing your markdown here..."
        />
      </div>
    );
  };

  return (
    <div 
      className={cn(
        'flex flex-col h-full bg-white',
        isFullscreen && 'fixed inset-0 z-50',
        className
      )}
      data-testid="markdown-viewer-pane"
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between p-4 border-b border-gray-200 space-y-3 md:space-y-0">
        <div className="flex items-center space-x-4 min-w-0">
          <h2 className="text-lg font-semibold text-gray-900">
            Markdown {isPreviewMode ? 'Preview' : 'Editor'}
          </h2>
          {document && (
            <span className="text-sm text-gray-500 flex-shrink-0">
              {document.markdownContent.length} characters
            </span>
          )}
        </div>
        
        {/* Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                <span className="hidden sm:inline">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span className="hidden sm:inline">Copy</span>
              </>
            )}
          </button>
          
          <div className="flex items-center space-x-1 border border-gray-300 rounded-lg">
            <button
              onClick={() => setIsPreviewMode(false)}
              className={cn(
                'flex items-center space-x-1 px-3 py-2 text-sm font-medium rounded-l-lg transition-colors',
                !isPreviewMode 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              <Edit className="w-4 h-4" />
              <span className="hidden sm:inline">Edit</span>
            </button>
            <button
              onClick={() => setIsPreviewMode(true)}
              className={cn(
                'flex items-center space-x-1 px-3 py-2 text-sm font-medium rounded-r-lg transition-colors',
                isPreviewMode 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              <Eye className="w-4 h-4" />
              <span className="hidden sm:inline">Preview</span>
            </button>
          </div>
          
          <div className="flex items-center space-x-1">
          <a 
            href={document?.markdownUrl} 
            download 
            className={cn(
              "flex items-center space-x-1 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
              document?.markdownUrl 
                ? "text-gray-700 bg-gray-100 hover:bg-gray-200" 
                : "text-gray-400 bg-gray-100 cursor-not-allowed opacity-50"
            )}
            onClick={!document?.markdownUrl ? (e) => e.preventDefault() : undefined}
            data-testid="download-markdown-btn"
          >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">Download</span>
            </a>
            <button
              onClick={() => handleExport('markdown')}
              disabled={!document}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">MD</span>
            </button>
            <button
              onClick={() => handleExport('json')}
              disabled={!document}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              <FileText className="w-4 h-4" />
              <span className="hidden sm:inline">JSON</span>
            </button>
          </div>

          <button
            onClick={toggleFullscreen}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {isPreviewMode ? renderPreview() : renderEditor()}
      </div>
    </div>
  );
}