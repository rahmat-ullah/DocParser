'use client';

import { useState, useCallback } from 'react';
import { Upload, File, X, FileText, Image } from 'lucide-react';
import { cn } from '@/lib/utils';
import { IconButton } from '@/components/ui/icon-button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
  className?: string;
}

export function FileUpload({ onFileSelect, isProcessing, className }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const clearFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-6 h-6 text-purple-500" />;
    }
    return <FileText className="w-6 h-6 text-primary" />;
  };

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-6 md:p-8 text-center transition-all duration-200',
          'hover:border-primary/50 hover:bg-primary/5',
          dragActive && 'border-primary bg-primary/10',
          isProcessing && 'pointer-events-none opacity-50',
          'border-border'
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf,.docx,.xlsx,.ppt,.pptx,.txt,.png,.jpg,.jpeg"
          onChange={handleFileSelect}
          disabled={isProcessing}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        {selectedFile ? (
          <div className="flex flex-col items-center space-y-4">
            <div className="flex items-center space-x-3 bg-background rounded-lg p-4 shadow-sm border max-w-full">
              {getFileIcon(selectedFile)}
              <div className="flex-1 text-left min-w-0">
                <p className="font-medium text-foreground truncate">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
              </div>
              <IconButton
                icon={<X className="w-4 h-4" />}
                onClick={clearFile}
                disabled={isProcessing}
                variant="ghost"
                size="xs"
                className="flex-shrink-0 hover:text-destructive"
                aria-label="Remove file"
              />
            </div>
            <p className="text-sm text-muted-foreground">
              {isProcessing ? 'Processing...' : 'File ready for processing'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-12 h-12 text-muted-foreground mx-auto" />
            <div>
              <p className="text-lg md:text-xl font-medium text-foreground">
                Drop your document here
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                or click to browse files
              </p>
            </div>
            <div className="text-xs text-muted-foreground">
              Supports: PDF, DOCX, XLSX, PPT, TXT, PNG, JPG (max 10MB)
            </div>
          </div>
        )}
      </div>
    </div>
  );
}