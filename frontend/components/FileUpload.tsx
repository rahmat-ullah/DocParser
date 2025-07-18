
'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { useUploadStore } from '@/hooks/useUploadStore';
import { useToast } from '@/hooks/use-toast';
import { 
  Upload, 
  File, 
  FileText, 
  Image, 
  FileSpreadsheet, 
  Presentation,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const FileUpload: React.FC = () => {
  const { uploadFile, isProcessing } = useUploadStore();
  const { toast } = useToast();
  const [dragActive, setDragActive] = useState(false);

  const getFileIcon = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf':
        return <FileText className="h-8 w-8 text-red-500" />;
      case 'docx':
        return <FileText className="h-8 w-8 text-blue-500" />;
      case 'xlsx':
        return <FileSpreadsheet className="h-8 w-8 text-green-500" />;
      case 'pptx':
        return <Presentation className="h-8 w-8 text-orange-500" />;
      case 'txt':
        return <FileText className="h-8 w-8 text-muted-foreground" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <Image className="h-8 w-8 text-purple-500" />;
      default:
        return <File className="h-8 w-8 text-muted-foreground" />;
    }
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setDragActive(false);
      
      if (acceptedFiles.length === 0) {
        toast({
          title: "Invalid file type",
          description: "Please upload a supported file format (PDF, DOCX, XLSX, PPTX, TXT, or image)",
          variant: "destructive",
        });
        return;
      }

      const file = acceptedFiles[0];
      
      // File size check (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please upload a file smaller than 50MB",
          variant: "destructive",
        });
        return;
      }

      try {
        await uploadFile(file);
        toast({
          title: "Upload successful",
          description: `${file.name} has been uploaded and is being processed`,
        });
      } catch (error) {
        toast({
          title: "Upload failed",
          description: error instanceof Error ? error.message : "An unknown error occurred",
          variant: "destructive",
        });
      }
    },
    [uploadFile, toast]
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif'],
    },
    maxFiles: 1,
    disabled: isProcessing,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragActive || dragActive
            ? 'border-primary bg-primary/5 scale-[1.02]'
            : 'border-border bg-background hover:border-primary/50 hover:bg-muted/50'
          }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className={`
            w-16 h-16 mx-auto rounded-full flex items-center justify-center transition-colors
            ${isDragActive || dragActive ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}
          `}>
            <Upload className="h-8 w-8" />
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-foreground">
              {isDragActive ? 'Drop your file here' : 'Upload your document'}
            </h3>
            <p className="text-sm text-muted-foreground">
              Drag and drop your file here, or click to select
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-2 text-xs text-muted-foreground">
            <span className="px-2 py-1 bg-muted rounded">PDF</span>
            <span className="px-2 py-1 bg-muted rounded">DOCX</span>
            <span className="px-2 py-1 bg-muted rounded">XLSX</span>
            <span className="px-2 py-1 bg-muted rounded">PPTX</span>
            <span className="px-2 py-1 bg-muted rounded">TXT</span>
            <span className="px-2 py-1 bg-muted rounded">Images</span>
          </div>

          {!isDragActive && !isProcessing && (
            <Button variant="outline" className="mt-4">
              Choose File
            </Button>
          )}
        </div>

        {acceptedFiles.length > 0 && (
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-3">
              {getFileIcon(acceptedFiles[0])}
              <div className="text-left">
                <p className="text-sm font-medium text-foreground">
                  {acceptedFiles[0].name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {(acceptedFiles[0].size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <CheckCircle className="h-5 w-5 text-green-500 ml-auto" />
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-muted-foreground">
          Maximum file size: 50MB
        </p>
      </div>
    </div>
  );
};

export default FileUpload;
