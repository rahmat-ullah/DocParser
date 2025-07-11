import { ParsedDocument } from '@/types/document';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export const fetchDocument = async (fileId: string): Promise<ParsedDocument> => {
  const response = await fetch(`${API_BASE_URL}/documents/${fileId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch document: ${response.statusText}`);
  }
  return response.json();
};

export const fetchDocumentHistory = async (): Promise<ParsedDocument[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/history`);
    if (!response.ok) {
      // If history endpoint doesn't exist, return empty array
      // The DocumentHistoryManager will handle local storage
      if (response.status === 404) {
        return [];
      }
      throw new Error(`Failed to fetch document history: ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    // Return empty array on network errors
    console.warn('History endpoint not available, using local storage', error);
    return [];
  }
};

export const uploadDocument = async (file: File): Promise<{ id: string; filename: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to upload document: ${error || response.statusText}`);
  }

  return response.json();
};

export const processDocument = async (documentId: string): Promise<{ message: string; document_id: string; status: string }> => {
  const response = await fetch(`${API_BASE_URL}/processing/${documentId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ enable_ai_processing: true }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to process document: ${error || response.statusText}`);
  }

  return response.json();
};

export const getProcessingStatus = async (documentId: string): Promise<{ document_id: string; status: string; error?: string; result?: string; markdown_url?: string }> => {
  const response = await fetch(`${API_BASE_URL}/processing/${documentId}/status`);
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get processing status: ${error || response.statusText}`);
  }
  return response.json();
};

export const getProcessingResult = async (documentId: string): Promise<{ document_id: string; extracted_text: string; ai_description: string; markdown_url?: string }> => {
  const response = await fetch(`${API_BASE_URL}/processing/${documentId}/result`);
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get processing result: ${error || response.statusText}`);
  }
  return response.json();
};

export const searchDocuments = async (query: string): Promise<ParsedDocument[]> => {
  const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`Failed to search documents: ${response.statusText}`);
  }
  return response.json();
};
