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
          'relative border-2 border-dashed rounded-2xl p-8 md:p-12 text-center transition-all duration-300',
          'hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/20',
          'hover:shadow-lg hover:shadow-blue-500/10',
          dragActive && 'border-blue-500 bg-blue-50 dark:bg-blue-950/30 shadow-lg shadow-blue-500/20',
          isProcessing && 'pointer-events-none opacity-50',
          'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800/50 backdrop-blur-sm',
          'shadow-sm'
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
          <div className="flex flex-col items-center space-y-6">
            <div className="flex items-center space-x-4 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md border border-slate-200 dark:border-slate-700 max-w-full">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-sm">
                {getFileIcon(selectedFile)}
              </div>
              <div className="flex-1 text-left min-w-0">
                <p className="font-semibold text-slate-900 dark:text-slate-100 truncate text-lg">{selectedFile.name}</p>
                <p className="text-slate-600 dark:text-slate-400 text-sm">{formatFileSize(selectedFile.size)}</p>
              </div>
              <IconButton
                icon={<X className="w-5 h-5" />}
                onClick={clearFile}
                disabled={isProcessing}
                variant="ghost"
                size="sm"
                className="flex-shrink-0 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg"
                aria-label="Remove file"
              />
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <p className="text-sm text-slate-600 dark:text-slate-400 font-medium">
                {isProcessing ? 'Processing document...' : 'Ready to process'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
              <Upload className="w-8 h-8 text-white" />
            </div>
            <div className="space-y-2">
              <p className="text-xl md:text-2xl font-semibold text-slate-900 dark:text-slate-100">
                Drop your document here
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                or click to browse files
              </p>
            </div>
            <div className="inline-flex items-center space-x-2 bg-slate-100 dark:bg-slate-700 px-4 py-2 rounded-full">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-slate-700 dark:text-slate-300 font-medium">
                PDF, DOCX, XLSX, PPT, TXT, PNG, JPG (max 10MB)
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}