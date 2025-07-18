
'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { useUploadStore } from '@/hooks/useUploadStore';
import { useToast } from '@/hooks/use-toast';
import { 
  FileText, 
  Image, 
  FileSpreadsheet, 
  Presentation, 
  Clock,
  MoreVertical,
  Download,
  Trash2
} from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';

interface DocumentHistoryItem {
  id: string;
  filename: string;
  file_type: string;
  created_at: string;
  processed: boolean;
}

const DocumentHistory: React.FC = () => {
  const { setSelectedDocument, selectedDocument } = useUploadStore();
  const { toast } = useToast();

  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['document-history'],
    queryFn: async (): Promise<DocumentHistoryItem[]> => {
      const response = await fetch('/api/history');
      if (!response.ok) {
        throw new Error('Failed to fetch document history');
      }
      return response.json();
    },
    refetchInterval: 5000,
  });

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-4 w-4 text-red-500" />;
      case 'docx':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'xlsx':
        return <FileSpreadsheet className="h-4 w-4 text-green-500" />;
      case 'pptx':
        return <Presentation className="h-4 w-4 text-orange-500" />;
      case 'txt':
        return <FileText className="h-4 w-4 text-muted-foreground" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <Image className="h-4 w-4 text-purple-500" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const handleDocumentClick = async (doc: DocumentHistoryItem) => {
    try {
      const response = await fetch(`/api/process?document_id=${doc.id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch document');
      }
      const documentData = await response.json();
      setSelectedDocument(documentData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load document",
        variant: "destructive",
      });
    }
  };

  const handleDownload = async (doc: DocumentHistoryItem) => {
    try {
      const response = await fetch(`/api/export?document_id=${doc.id}&format=markdown`);
      if (!response.ok) {
        throw new Error('Failed to download document');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${doc.filename.split('.')[0]}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download document",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-16 bg-muted rounded-lg"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <div className="text-sm text-muted-foreground">
          Failed to load document history
        </div>
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="p-4 text-center space-y-3">
        <div className="w-12 h-12 mx-auto bg-muted rounded-full flex items-center justify-center">
          <Clock className="h-6 w-6 text-muted-foreground" />
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium text-foreground">No documents yet</p>
          <p className="text-xs text-muted-foreground">
            Upload your first document to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-3 space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className={`
            group relative p-3 rounded-lg border cursor-pointer transition-all duration-200
            ${selectedDocument?.id === doc.id
              ? 'bg-primary/10 border-primary shadow-sm'
              : 'bg-background border-border hover:bg-muted/50 hover:border-border'
            }
          `}
          onClick={() => handleDocumentClick(doc)}
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              {getFileIcon(doc.file_type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground truncate">
                    {doc.filename}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-muted-foreground uppercase tracking-wide">
                      {doc.file_type}
                    </span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(doc.created_at)}
                    </span>
                  </div>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreVertical className="h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-40">
                    <DropdownMenuItem onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(doc);
                    }}>
                      <Download className="h-3 w-3 mr-2" />
                      Download
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      className="text-destructive"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Trash2 className="h-3 w-3 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              
              {!doc.processed && (
                <div className="mt-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-orange-600">Processing...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentHistory;
