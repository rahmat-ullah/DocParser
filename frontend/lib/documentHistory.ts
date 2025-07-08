import { ParsedDocument, DocumentHistory } from '@/types/document';

const STORAGE_KEY = 'document-parser-history';

export class DocumentHistoryManager {
  private static instance: DocumentHistoryManager;
  private history: DocumentHistory;

  private constructor() {
    this.history = this.loadHistory();
  }

  public static getInstance(): DocumentHistoryManager {
    if (!DocumentHistoryManager.instance) {
      DocumentHistoryManager.instance = new DocumentHistoryManager();
    }
    return DocumentHistoryManager.instance;
  }

  public addDocument(document: ParsedDocument): void {
    // Remove existing document with same ID
    this.history.documents = this.history.documents.filter(doc => doc.id !== document.id);
    
    // Add new document to the beginning
    this.history.documents.unshift(document);
    
    // Keep only last 50 documents
    if (this.history.documents.length > 50) {
      this.history.documents = this.history.documents.slice(0, 50);
    }
    
    this.history.lastAccessed = new Date();
    this.saveHistory();
  }

  public getDocuments(): ParsedDocument[] {
    return this.history.documents;
  }

  public getDocument(id: string): ParsedDocument | undefined {
    return this.history.documents.find(doc => doc.id === id);
  }

  public removeDocument(id: string): void {
    this.history.documents = this.history.documents.filter(doc => doc.id !== id);
    this.saveHistory();
  }

  public clearHistory(): void {
    this.history = {
      documents: [],
      lastAccessed: new Date()
    };
    this.saveHistory();
  }

  public searchDocuments(query: string): ParsedDocument[] {
    const lowercaseQuery = query.toLowerCase();
    return this.history.documents.filter(doc => 
      doc.metadata.name.toLowerCase().includes(lowercaseQuery) ||
      doc.markdownContent.toLowerCase().includes(lowercaseQuery)
    );
  }

  private loadHistory(): DocumentHistory {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return {
          documents: parsed.documents || [],
          lastAccessed: new Date(parsed.lastAccessed || Date.now())
        };
      }
    } catch (error) {
      console.error('Failed to load document history:', error);
    }
    
    return {
      documents: [],
      lastAccessed: new Date()
    };
  }

  private saveHistory(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.history));
    } catch (error) {
      console.error('Failed to save document history:', error);
    }
  }
}