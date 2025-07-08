import { ParsedDocument } from '@/types/document';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export const fetchDocument = async (fileId: string): Promise<ParsedDocument> => {
  const response = await fetch(`${API_BASE_URL}/documents/${fileId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch document: ${response.statusText}`);
  }
  return response.json();
};

export const fetchDocumentHistory = async (): Promise<ParsedDocument[]> => {
  const response = await fetch(`${API_BASE_URL}/history`);
  if (!response.ok) {
    throw new Error(`Failed to fetch document history: ${response.statusText}`);
  }
  return response.json();
};

export const uploadDocument = async (file: File): Promise<{ id: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Failed to upload document: ${response.statusText}`);
  }

  return response.json();
};

export const processDocument = async (fileId: string): Promise<ParsedDocument> => {
  const response = await fetch(`${API_BASE_URL}/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ fileId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to process document: ${response.statusText}`);
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
