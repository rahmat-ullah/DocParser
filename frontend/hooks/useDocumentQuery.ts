import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { fetchDocument, fetchDocumentHistory } from '@/lib/documentApi';
import { ParsedDocument } from '@/types/document';
import { useCallback } from 'react';

// Document Query Hook with optimistic UI and memory-safe caching
export const useDocumentQuery = (fileId: string | null, options?: {
  enabled?: boolean;
  suspense?: boolean;
  select?: (data: ParsedDocument) => any;
}) => {
  const queryClient = useQueryClient();
  const { enabled = true, suspense = false, select } = options || {};

  const query = useQuery<ParsedDocument, Error>({
    queryKey: ['document', fileId],
    queryFn: () => {
      if (!fileId) throw new Error('File ID is required');
      return fetchDocument(fileId);
    },
    enabled: enabled && !!fileId,
    staleTime: 1000 * 60 * 10, // 10 minutes
    cacheTime: 1000 * 60 * 60, // 1 hour
    suspense,
    useErrorBoundary: true,
    select,
    // Lazy loading for large markdown content
    structuralSharing: false, // Disable to prevent memory issues with large strings
    onSuccess: (data) => {
      // Prefetch related data
      queryClient.prefetchQuery(['documentHistory'], fetchDocumentHistory, {
        staleTime: 1000 * 60 * 5,
      });
    },
  });

  const invalidateDocument = useCallback(() => {
    queryClient.invalidateQueries(['document', fileId]);
  }, [queryClient, fileId]);

  const refetchDocument = useCallback(() => {
    return query.refetch();
  }, [query]);

  const removeDocument = useCallback(() => {
    queryClient.removeQueries(['document', fileId]);
  }, [queryClient, fileId]);

  return {
    ...query,
    invalidateDocument,
    refetchDocument,
    removeDocument,
  };
};

// Document History Query Hook
export const useDocumentHistoryQuery = (options?: {
  enabled?: boolean;
  suspense?: boolean;
}) => {
  const queryClient = useQueryClient();
  const { enabled = true, suspense = false } = options || {};

  const query = useQuery<ParsedDocument[], Error>({
    queryKey: ['documentHistory'],
    queryFn: fetchDocumentHistory,
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 30, // 30 minutes
    suspense,
    useErrorBoundary: false, // Handle errors gracefully for history
  });

  const invalidateHistory = useCallback(() => {
    queryClient.invalidateQueries(['documentHistory']);
  }, [queryClient]);

  const addDocumentToHistory = useCallback((document: ParsedDocument) => {
    queryClient.setQueryData<ParsedDocument[]>(['documentHistory'], (old) => {
      if (!old) return [document];
      // Remove duplicate if exists and add to beginning
      const filtered = old.filter(doc => doc.id !== document.id);
      return [document, ...filtered];
    });
  }, [queryClient]);

  const removeDocumentFromHistory = useCallback((documentId: string) => {
    queryClient.setQueryData<ParsedDocument[]>(['documentHistory'], (old) => {
      if (!old) return [];
      return old.filter(doc => doc.id !== documentId);
    });
  }, [queryClient]);

  return {
    ...query,
    invalidateHistory,
    addDocumentToHistory,
    removeDocumentFromHistory,
  };
};

// Mutation for updating document content optimistically
export const useUpdateDocumentMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<ParsedDocument, Error, { fileId: string; updates: Partial<ParsedDocument> }>({
    mutationFn: async ({ fileId, updates }) => {
      // In a real app, this would make an API call
      const response = await fetch(`/api/documents/${fileId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (!response.ok) throw new Error('Failed to update document');
      return response.json();
    },
    onMutate: async ({ fileId, updates }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries(['document', fileId]);
      
      // Snapshot the previous value
      const previousDocument = queryClient.getQueryData<ParsedDocument>(['document', fileId]);
      
      // Optimistically update the document
      if (previousDocument) {
        queryClient.setQueryData<ParsedDocument>(['document', fileId], {
          ...previousDocument,
          ...updates,
        });
      }
      
      return { previousDocument };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousDocument) {
        queryClient.setQueryData(['document', variables.fileId], context.previousDocument);
      }
    },
    onSettled: (data, error, variables) => {
      // Always refetch after mutation
      queryClient.invalidateQueries(['document', variables.fileId]);
    },
  });
};

