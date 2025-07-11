export interface DocumentMetadata {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: Date;
  lastModified: Date;
}

export interface ParsedDocument {
  id: string;
  metadata: DocumentMetadata;
  originalContent: string;
  markdownContent: string;
  markdownUrl?: string;
  sections: DocumentSection[];
}

export interface DocumentSection {
  id: string;
  title: string;
  content: string;
  startIndex: number;
  endIndex: number;
  level: number;
}

export interface DocumentHistory {
  documents: ParsedDocument[];
  lastAccessed: Date;
}

export type SupportedFileType = 'pdf' | 'docx' | 'xlsx' | 'ppt' | 'txt' | 'png' | 'jpg' | 'jpeg';

export interface ParsingProgress {
  stage: 'uploading' | 'parsing' | 'converting' | 'complete';
  progress: number;
  message: string;
  documentId?: string;
  timestamp?: string;
}
