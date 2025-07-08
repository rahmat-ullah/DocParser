'use client';

import { Suspense, ReactNode } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { RefreshCw, AlertTriangle } from 'lucide-react';

interface DocumentSuspenseProps {
  children: ReactNode;
  fallback?: ReactNode;
  errorFallback?: ReactNode;
  onRetry?: () => void;
}

// Loading skeleton for document content
const DocumentLoadingSkeleton = () => (
  <div className="space-y-4 p-6">
    <div className="space-y-2">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
    </div>
    <div className="space-y-2">
      <Skeleton className="h-6 w-1/2" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-4/5" />
      <Skeleton className="h-4 w-3/4" />
    </div>
    <div className="space-y-2">
      <Skeleton className="h-6 w-2/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  </div>
);

// Error fallback component
const DocumentErrorFallback = ({ 
  error, 
  resetErrorBoundary, 
  onRetry 
}: { 
  error: Error; 
  resetErrorBoundary: () => void;
  onRetry?: () => void;
}) => (
  <div className="flex flex-col items-center justify-center p-8 space-y-4">
    <AlertTriangle className="w-12 h-12 text-destructive" />
    <div className="text-center space-y-2">
      <h3 className="text-lg font-semibold text-foreground">
        Failed to load document
      </h3>
      <p className="text-sm text-muted-foreground max-w-md">
        {error.message || 'An unexpected error occurred while loading the document.'}
      </p>
    </div>
    <div className="flex space-x-2">
      <Button 
        variant="outline" 
        size="sm" 
        onClick={() => {
          resetErrorBoundary();
          onRetry?.();
        }}
        className="flex items-center space-x-2"
      >
        <RefreshCw className="w-4 h-4" />
        <span>Retry</span>
      </Button>
    </div>
  </div>
);

export function DocumentSuspense({ 
  children, 
  fallback,
  errorFallback,
  onRetry 
}: DocumentSuspenseProps) {
  return (
    <ErrorBoundary
      FallbackComponent={(props) => 
        errorFallback || (
          <DocumentErrorFallback {...props} onRetry={onRetry} />
        )
      }
      onReset={onRetry}
      resetKeys={[children]} // Reset when children change
    >
      <Suspense fallback={fallback || <DocumentLoadingSkeleton />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

// Memory-safe document wrapper that only loads visible content
export function LazyDocumentContent({ 
  documentId, 
  isVisible = true,
  children 
}: { 
  documentId: string;
  isVisible?: boolean;
  children: ReactNode;
}) {
  if (!isVisible) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-sm text-muted-foreground">
          Document content not loaded to save memory
        </div>
      </div>
    );
  }

  return (
    <DocumentSuspense>
      {children}
    </DocumentSuspense>
  );
}
