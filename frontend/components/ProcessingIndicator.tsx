'use client';

import { useState, useEffect } from 'react';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { ParsingProgress } from '@/types/document';
import { cn } from '@/lib/utils';

interface ProcessingIndicatorProps {
  progress: ParsingProgress;
  className?: string;
}

export function ProcessingIndicator({ progress, className }: ProcessingIndicatorProps) {
  const [displayedProgress, setDisplayedProgress] = useState(0);

  useEffect(() => {
    // Smooth progress animation
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
  }, [progress.progress]);

  const getStageIcon = () => {
    switch (progress.stage) {
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
    switch (progress.stage) {
      case 'complete':
        return 'bg-green-500';
      case 'uploading':
        return 'bg-blue-500';
      case 'parsing':
        return 'bg-yellow-500';
      case 'converting':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStageText = () => {
    switch (progress.stage) {
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
    <div className={cn('bg-white rounded-lg border border-gray-200 p-6 shadow-sm', className)}>
      <div className="flex items-center space-x-4 mb-4">
        {getStageIcon()}
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">{getStageText()}</h3>
          <p className="text-sm text-gray-600">{progress.message}</p>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="relative">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={cn(
              'h-2 rounded-full transition-all duration-300 ease-out',
              getStageColor()
            )}
            style={{ width: `${displayedProgress}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0%</span>
          <span className="font-medium">{Math.round(displayedProgress)}%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="flex justify-between mt-4">
        {[
          { key: 'uploading', label: 'Upload' },
          { key: 'parsing', label: 'Parse' },
          { key: 'converting', label: 'Convert' },
          { key: 'complete', label: 'Complete' }
        ].map((stage, index) => (
          <div
            key={stage.key}
            className={cn(
              'flex flex-col items-center space-y-1',
              progress.stage === stage.key ? 'text-primary' : 'text-gray-400'
            )}
          >
            <div
              className={cn(
                'w-3 h-3 rounded-full border-2 transition-colors',
                progress.stage === stage.key 
                  ? 'border-primary bg-primary' 
                  : index < ['uploading', 'parsing', 'converting', 'complete'].indexOf(progress.stage)
                  ? 'border-green-500 bg-green-500'
                  : 'border-gray-300 bg-white'
              )}
            />
            <span className="text-xs font-medium">{stage.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}