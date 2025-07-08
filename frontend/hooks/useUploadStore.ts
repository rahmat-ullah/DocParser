import { create } from 'zustand';
import { ParsedDocument, DocumentSection, ParsingProgress } from '@/types/document';

interface UploadStore {
  // UI State
  currentDocument: ParsedDocument | null;
  selectedSection: DocumentSection | null;
  isProcessing: boolean;
  processingProgress: ParsingProgress;
  showHistory: boolean;
  showSettings: boolean;
  isMobile: boolean;
  
  // UI Actions
  setCurrentDocument: (doc: ParsedDocument | null) => void;
  setSelectedSection: (section: DocumentSection | null) => void;
  setIsProcessing: (processing: boolean) => void;
  setProcessingProgress: (progress: ParsingProgress) => void;
  setShowHistory: (show: boolean) => void;
  setShowSettings: (show: boolean) => void;
  setIsMobile: (mobile: boolean) => void;
  
  // Combined Actions
  toggleHistory: () => void;
  toggleSettings: () => void;
  resetUploadState: () => void;
  selectDocumentWithSection: (doc: ParsedDocument) => void;
}

export const useUploadStore = create<UploadStore>((set, get) => ({
  // Initial State
  currentDocument: null,
  selectedSection: null,
  isProcessing: false,
  processingProgress: {
    stage: 'uploading',
    progress: 0,
    message: 'Initializing...'
  },
  showHistory: true,
  showSettings: false,
  isMobile: false,
  
  // UI Actions
  setCurrentDocument: (doc) => set(() => ({ currentDocument: doc })),
  setSelectedSection: (section) => set(() => ({ selectedSection: section })),
  setIsProcessing: (processing) => set(() => ({ isProcessing: processing })),
  setProcessingProgress: (progress) => set(() => ({ processingProgress: progress })),
  setShowHistory: (show) => set(() => ({ showHistory: show })),
  setShowSettings: (show) => set(() => ({ showSettings: show })),
  setIsMobile: (mobile) => set(() => ({ isMobile: mobile })),
  
  // Combined Actions
  toggleHistory: () => set((state) => ({ showHistory: !state.showHistory })),
  toggleSettings: () => set((state) => ({ showSettings: !state.showSettings })),
  
  resetUploadState: () => set(() => ({
    currentDocument: null,
    selectedSection: null,
    isProcessing: false,
    processingProgress: {
      stage: 'uploading',
      progress: 0,
      message: 'Initializing...'
    }
  })),
  
  selectDocumentWithSection: (doc) => set(() => ({
    currentDocument: doc,
    selectedSection: doc.sections[0] || null,
    showHistory: get().isMobile ? false : get().showHistory
  })),
}));
