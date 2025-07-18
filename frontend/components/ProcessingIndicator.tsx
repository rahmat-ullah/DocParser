'use client';

import { useState, useEffect } from 'react';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { ParsingProgress } from '@/types/document';
import { cn } from '@/lib/utils';
import { useSocketProgress } from '@/hooks/useSocketProgress';

interface ProcessingIndicatorProps {
  progress: ParsingProgress;
  className?: string;
}

export function ProcessingIndicator({ progress, className }: ProcessingIndicatorProps) {
  const [displayedProgress, setDisplayedProgress] = useState(0);
  const [currentProgress, setCurrentProgress] = useState(progress);

  // Use Socket.IO hook for real-time updates
  const { lastProgress, isConnected } = useSocketProgress({
    documentId: progress.documentId,
    onProgress: (data) => {
      setCurrentProgress(data);
      setDisplayedProgress(data.progress);
    },
    autoConnect: !!progress.documentId
  });

  useEffect(() => {
    if (!progress.documentId || !isConnected) {
      // Fallback to smooth progress animation if no documentId or not connected
      const interval = setInterval(() => {
        setDisplayedProgress(prev => {
          const diff = progress.progress - prev;
          if (Math.abs(diff) < 1) {
            clearInterval(interval);
            return progress.progress;
          }
          return prev + diff * 0.1;
        });
      }, 50);
      return () => clearInterval(interval);
    }
  }, [progress.progress, progress.documentId, isConnected]);

  // Use real-time progress if available, otherwise use prop progress
  const activeProgress = lastProgress || currentProgress;

  const getStageIcon = () => {
    switch (activeProgress.stage) {
      case 'complete':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'uploading':
      case 'parsing':
      case 'converting':
        return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
      default:
        return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getStageColor = () => {
    switch (activeProgress.stage) {
      case 'complete':
        return 'bg-green-500';
      case 'uploading':
        return 'bg-blue-500';
      case 'parsing':
        return 'bg-yellow-500';
      case 'converting':
        return 'bg-purple-500';
      default:
        return 'bg-muted-foreground';
    }
  };

  const getStageText = () => {
    switch (activeProgress.stage) {
      case 'uploading':
        return 'Uploading file...';
      case 'parsing':
        return 'Parsing document...';
      case 'converting':
        return 'Converting to markdown...';
      case 'complete':
        return 'Processing complete!';
      default:
        return 'Processing...';
    }
  };

  return (
    <div className={cn('bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-8 shadow-lg backdrop-blur-sm', className)}>
      <div className="flex items-center space-x-4 mb-6">
        <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-sm">
          {getStageIcon()}
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">{getStageText()}</h3>
          <p className="text-slate-600 dark:text-slate-400 mt-1">{activeProgress.message}</p>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="relative mb-6">
        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all duration-500 ease-out relative',
              getStageColor()
            )}
            style={{ width: `${displayedProgress}%` }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent rounded-full"></div>
          </div>
        </div>
        <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400 mt-2">
          <span>0%</span>
          <span className="font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {Math.round(displayedProgress)}%
          </span>
          <span>100%</span>
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="flex justify-between">
        {[
          { key: 'uploading', label: 'Upload' },
          { key: 'parsing', label: 'Parse' },
          { key: 'converting', label: 'Convert' },
          { key: 'complete', label: 'Complete' }
        ].map((stage, index) => (
          <div
            key={stage.key}
            className={cn(
              'flex flex-col items-center space-y-2',
              activeProgress.stage === stage.key ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500'
            )}
          >
            <div
              className={cn(
                'w-4 h-4 rounded-full border-2 transition-all duration-300',
                activeProgress.stage === stage.key 
                  ? 'border-blue-500 bg-blue-500 shadow-lg shadow-blue-500/30' 
                  : index < ['uploading', 'parsing', 'converting', 'complete'].indexOf(activeProgress.stage)
                  ? 'border-green-500 bg-green-500 shadow-sm shadow-green-500/20'
                  : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800'
              )}
            >
              {(activeProgress.stage === stage.key || index < ['uploading', 'parsing', 'converting', 'complete'].indexOf(activeProgress.stage)) && (
                <div className="w-full h-full rounded-full bg-white/30 animate-pulse"></div>
              )}
            </div>
            <span className="text-xs font-medium">{stage.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}