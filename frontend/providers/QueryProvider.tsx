'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, ReactNode } from 'react';

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Stale time - how long data is considered fresh
            staleTime: 1000 * 60 * 5, // 5 minutes
            // Cache time - how long data stays in cache when unused
            cacheTime: 1000 * 60 * 30, // 30 minutes
            // Enable suspense for all queries by default
            suspense: false, // We'll enable this per query where needed
            // Retry configuration
            retry: (failureCount, error) => {
              // Don't retry on 4xx errors
              if (error instanceof Error && error.message.includes('4')) {
                return false;
              }
              return failureCount < 3;
            },
            // Refetch on window focus
            refetchOnWindowFocus: false,
            // Background refetching
            refetchOnMount: true,
            // Error boundary integration
            useErrorBoundary: false, // We'll handle this per query
          },
          mutations: {
            // Global mutation options
            retry: 1,
            useErrorBoundary: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
