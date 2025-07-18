
'use client';

import React from 'react';
import { Progress } from '@/components/ui/progress';
import { useUploadStore } from '@/hooks/useUploadStore';
import { 
  Upload, 
  FileText, 
  Brain, 
  CheckCircle, 
  Loader2 
} from 'lucide-react';

const ProcessingIndicator: React.FC = () => {
  const { processingStage, processingProgress, isProcessing } = useUploadStore();

  const stages = [
    { 
      key: 'uploading', 
      icon: Upload, 
      label: 'Uploading file', 
      description: 'Transferring your document securely'
    },
    { 
      key: 'parsing', 
      icon: FileText, 
      label: 'Parsing document', 
      description: 'Extracting content and structure'
    },
    { 
      key: 'ai_processing', 
      icon: Brain, 
      label: 'AI processing', 
      description: 'Analyzing content with AI'
    },
    { 
      key: 'generating_markdown', 
      icon: FileText, 
      label: 'Generating markdown', 
      description: 'Creating formatted output'
    },
    { 
      key: 'complete', 
      icon: CheckCircle, 
      label: 'Complete', 
      description: 'Processing finished successfully'
    }
  ];

  const currentStageIndex = stages.findIndex(stage => stage.key === processingStage);
  const progress = processingProgress || 0;

  if (!isProcessing && processingStage !== 'complete') {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="w-12 h-12 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
          <Loader2 className="h-6 w-6 text-primary animate-spin" />
        </div>
        <h3 className="text-lg font-semibold text-foreground">
          Processing Document
        </h3>
        <p className="text-sm text-muted-foreground">
          Please wait while we convert your document
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Stages */}
      <div className="space-y-3">
        {stages.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = index === currentStageIndex;
          const isCompleted = index < currentStageIndex;
          const isCurrent = processingStage === stage.key;

          return (
            <div
              key={stage.key}
              className={`
                flex items-start gap-3 p-3 rounded-lg transition-all duration-200
                ${isActive || isCurrent 
                  ? 'bg-primary/5 border border-primary/20' 
                  : isCompleted 
                    ? 'bg-muted/50' 
                    : 'opacity-50'
                }
              `}
            >
              <div className={`
                flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-colors
                ${isActive || isCurrent
                  ? 'bg-primary text-primary-foreground'
                  : isCompleted
                    ? 'bg-green-500 text-white'
                    : 'bg-muted text-muted-foreground'
                }
              `}>
                {isCompleted ? (
                  <CheckCircle className="h-4 w-4" />
                ) : isActive || isCurrent ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className={`
                  text-sm font-medium
                  ${isActive || isCurrent || isCompleted 
                    ? 'text-foreground' 
                    : 'text-muted-foreground'
                  }
                `}>
                  {stage.label}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {stage.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Current Stage Detail */}
      {processingStage && (
        <div className="text-center p-3 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground">
            Current: {stages.find(s => s.key === processingStage)?.label || processingStage}
          </p>
        </div>
      )}
    </div>
  );
};

export default ProcessingIndicator;
