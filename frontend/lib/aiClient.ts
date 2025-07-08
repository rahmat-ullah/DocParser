import OpenAI from 'openai';

// Types for better type safety
interface AIClientConfig {
  apiKey: string;
  baseURL?: string;
  maxRetries?: number;
  timeout?: number;
  dangerouslyAllowBrowser?: boolean;
}

interface RateLimitConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
}

interface StreamingOptions {
  onChunk?: (chunk: string) => void;
  onComplete?: (fullText: string) => void;
  onError?: (error: Error) => void;
  onProgress?: (progress: number) => void;
}

interface MatrixData {
  [key: string]: string | number;
}

interface ImageAnalysisOptions {
  model?: string;
  maxTokens?: number;
  detail?: 'low' | 'high' | 'auto';
  customPrompt?: string;
}

interface LaTeXExtractionOptions {
  model?: string;
  includeInlineFormulas?: boolean;
  preserveFormatting?: boolean;
  replaceWithPlaceholders?: boolean;
}

interface TableGenerationOptions {
  model?: string;
  includeHeaders?: boolean;
  formatNumbers?: boolean;
  customInstructions?: string;
  alignment?: 'left' | 'center' | 'right'[];
  sortBy?: string;
}

export class AIClient {
  private client: OpenAI;
  private rateLimitConfig: RateLimitConfig;

  constructor(config: AIClientConfig) {
    // Security warning for browser usage
    if (typeof window !== 'undefined' && config.dangerouslyAllowBrowser) {
      console.warn(
        '⚠️  WARNING: You are using OpenAI API in the browser. ' +
        'This exposes your API key to users. Consider using a backend proxy instead.'
      );
    }

    this.client = new OpenAI({
      apiKey: config.apiKey,
      baseURL: config.baseURL,
      maxRetries: config.maxRetries || 3,
      timeout: config.timeout || 30000,
      dangerouslyAllowBrowser: config.dangerouslyAllowBrowser || true,
    });

    this.rateLimitConfig = {
      maxRetries: 5,
      baseDelay: 1000,
      maxDelay: 30000,
      backoffFactor: 2,
    };
  }

  /**
   * Execute OpenAI API call with automatic rate-limit back-off
   */
  private async executeWithBackoff<T>(
    operation: () => Promise<T>,
    attempt: number = 0
  ): Promise<T> {
    try {
      return await operation();
    } catch (error: any) {
      // Check if it's a rate limit error
      if (
        error?.status === 429 &&
        attempt < this.rateLimitConfig.maxRetries
      ) {
        const delay = Math.min(
          this.rateLimitConfig.baseDelay * Math.pow(this.rateLimitConfig.backoffFactor, attempt),
          this.rateLimitConfig.maxDelay
        );
        
        console.warn(`Rate limit hit, retrying in ${delay}ms... (attempt ${attempt + 1})`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.executeWithBackoff(operation, attempt + 1);
      }
      
      // Re-throw non-rate-limit errors or if max retries exceeded
      throw error;
    }
  }

  /**
   * Basic chat completion with rate limiting
   */
  async chatCompletion(
    messages: OpenAI.ChatCompletionMessageParam[],
    options: {
      model?: string;
      temperature?: number;
      maxTokens?: number;
      stream?: boolean;
    } = {}
  ): Promise<OpenAI.ChatCompletionMessage> {
    const response = await this.executeWithBackoff(async () => {
      return this.client.chat.completions.create({
        model: options.model || 'gpt-4o-mini',
        messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens,
        stream: options.stream || false,
      });
    });

    if ('choices' in response) {
      return response.choices[0].message;
    }
    
    throw new Error('Invalid response format');
  }

  /**
   * Streaming chat completion with rate limiting
   */
  async streamChatCompletion(
    messages: OpenAI.ChatCompletionMessageParam[],
    streamingOptions: StreamingOptions,
    options: {
      model?: string;
      temperature?: number;
      maxTokens?: number;
    } = {}
  ): Promise<void> {
    try {
      const stream = await this.executeWithBackoff(async () => {
        return this.client.chat.completions.create({
          model: options.model || 'gpt-4o-mini',
          messages,
          temperature: options.temperature || 0.7,
          max_tokens: options.maxTokens,
          stream: true,
        });
      });

      let fullText = '';

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content || '';
        if (content) {
          fullText += content;
          streamingOptions.onChunk?.(content);
        }
      }

      streamingOptions.onComplete?.(fullText);
    } catch (error) {
      streamingOptions.onError?.(error as Error);
    }
  }

  /**
   * Describe an image from base64 data
   */
  async describeImage(
    base64Data: string,
    options: ImageAnalysisOptions = {}
  ): Promise<string> {
    const prompt = options.customPrompt || "Please describe this image in detail.";
    
    const messages: OpenAI.ChatCompletionMessageParam[] = [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: prompt,
          },
          {
            type: "image_url",
            image_url: {
              url: `data:image/jpeg;base64,${base64Data}`,
              detail: options.detail || 'auto',
            },
          },
        ],
      },
    ];

    const response = await this.chatCompletion(messages, {
      model: options.model || 'gpt-4o-mini',
      maxTokens: options.maxTokens || 1000,
    });

    return response.content || '';
  }

  /**
   * Extract LaTeX from a text block
   */
  async extractLatex(
    textBlock: string,
    options: LaTeXExtractionOptions = {}
  ): Promise<{
    latex: string[];
    processedText: string;
  }> {
    const includeInline = options.includeInlineFormulas ?? true;
    const preserveFormatting = options.preserveFormatting ?? true;
    const replaceWithPlaceholders = options.replaceWithPlaceholders ?? true;
    
    const prompt = `
Please extract all LaTeX mathematical expressions from the following text block.
${includeInline ? 'Include both inline formulas (\\(...\\) or $...$) and display formulas (\\[...\\] or $$...$$).' : 'Focus on display formulas (\\[...\\] or $$...$$) only.'}
${preserveFormatting ? 'Preserve original formatting and spacing.' : 'Clean up formatting for better readability.'}

Return the result as a JSON object with:
- "latex": an array of all LaTeX expressions found
- "processedText": the original text ${replaceWithPlaceholders ? 'with LaTeX expressions replaced by placeholder markers like [MATH_1], [MATH_2], etc.' : 'with LaTeX expressions removed'}

Text block:
${textBlock}
    `;

    const messages: OpenAI.ChatCompletionMessageParam[] = [
      {
        role: "user",
        content: prompt,
      },
    ];

    const response = await this.chatCompletion(messages, {
      model: options.model || 'gpt-4o-mini',
      maxTokens: 2000,
    });

    try {
      const result = JSON.parse(response.content || '{}');
      return {
        latex: result.latex || [],
        processedText: result.processedText || textBlock,
      };
    } catch (error) {
      console.error('Failed to parse LaTeX extraction result:', error);
      return {
        latex: [],
        processedText: textBlock,
      };
    }
  }

  /**
   * Generate a markdown table from a matrix of data
   */
  async markdownTableFromMatrix(
    matrix: MatrixData[],
    options: TableGenerationOptions = {}
  ): Promise<string> {
    if (!matrix || matrix.length === 0) {
      return '';
    }

    const includeHeaders = options.includeHeaders ?? true;
    const formatNumbers = options.formatNumbers ?? false;
    const alignment = options.alignment || [];
    const sortBy = options.sortBy;

    let instructions = [];
    if (includeHeaders) {
      instructions.push('- Use the first row as headers if appropriate');
    } else {
      instructions.push('- Do not include headers');
    }
    
    if (formatNumbers) {
      instructions.push('- Format numbers appropriately (e.g., add commas for thousands, limit decimal places)');
    } else {
      instructions.push('- Keep numbers as-is');
    }
    
    if (alignment.length > 0) {
      instructions.push(`- Column alignment: ${alignment.join(', ')}`);
    }
    
    if (sortBy) {
      instructions.push(`- Sort the data by column: ${sortBy}`);
    }
    
    if (options.customInstructions) {
      instructions.push(`- Additional instructions: ${options.customInstructions}`);
    }

    const prompt = `
Please convert the following data matrix into a well-formatted markdown table.

Instructions:
${instructions.join('\n')}

Data matrix:
${JSON.stringify(matrix, null, 2)}

Return only the markdown table without any additional explanation.
    `;

    const messages: OpenAI.ChatCompletionMessageParam[] = [
      {
        role: "user",
        content: prompt,
      },
    ];

    const response = await this.chatCompletion(messages, {
      model: options.model || 'gpt-4o-mini',
      maxTokens: 1500,
    });

    return response.content || '';
  }

  /**
   * Utility method to convert file to base64 (for browser usage)
   */
  static async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        // Remove data:image/...;base64, prefix
        resolve(base64.split(',')[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * Get the current rate limit status (estimated)
   */
  getRateLimitConfig(): RateLimitConfig {
    return { ...this.rateLimitConfig };
  }

  /**
   * Update rate limit configuration
   */
  updateRateLimitConfig(config: Partial<RateLimitConfig>): void {
    this.rateLimitConfig = { ...this.rateLimitConfig, ...config };
  }

  /**
   * Analyze document structure and extract sections
   */
  async analyzeDocumentStructure(
    documentText: string,
    options: {
      model?: string;
      extractTables?: boolean;
      extractImages?: boolean;
      extractFormulas?: boolean;
    } = {}
  ): Promise<{
    sections: Array<{
      title: string;
      content: string;
      type: 'header' | 'paragraph' | 'list' | 'table' | 'formula' | 'other';
      level?: number;
    }>;
    metadata: {
      totalSections: number;
      hasFormulas: boolean;
      hasTables: boolean;
      estimatedReadingTime: number;
    };
  }> {
    const prompt = `
Please analyze the following document and break it down into structured sections.

Extract the following information:
1. Document sections with their titles, content, and types
2. Identify headers at different levels
3. ${options.extractTables ? 'Identify and extract table data' : 'Note presence of tables'}
4. ${options.extractFormulas ? 'Identify and extract mathematical formulas' : 'Note presence of formulas'}
5. ${options.extractImages ? 'Identify image references and descriptions' : 'Note presence of images'}

Return as JSON with sections array and metadata object.

Document text:
${documentText}
    `;

    const messages: OpenAI.ChatCompletionMessageParam[] = [
      {
        role: "user",
        content: prompt,
      },
    ];

    const response = await this.chatCompletion(messages, {
      model: options.model || 'gpt-4o-mini',
      maxTokens: 3000,
    });

    try {
      const result = JSON.parse(response.content || '{}');
      return {
        sections: result.sections || [],
        metadata: {
          totalSections: result.sections?.length || 0,
          hasFormulas: result.metadata?.hasFormulas || false,
          hasTables: result.metadata?.hasTables || false,
          estimatedReadingTime: result.metadata?.estimatedReadingTime || 0,
          ...result.metadata,
        },
      };
    } catch (error) {
      console.error('Failed to parse document structure analysis:', error);
      return {
        sections: [],
        metadata: {
          totalSections: 0,
          hasFormulas: false,
          hasTables: false,
          estimatedReadingTime: 0,
        },
      };
    }
  }

  /**
   * Summarize document content
   */
  async summarizeDocument(
    documentText: string,
    options: {
      model?: string;
      maxLength?: 'short' | 'medium' | 'long';
      focusAreas?: string[];
      includeKeyPoints?: boolean;
    } = {}
  ): Promise<{
    summary: string;
    keyPoints?: string[];
    topics: string[];
  }> {
    const lengthInstruction = {
      short: 'in 2-3 sentences',
      medium: 'in 1-2 paragraphs',
      long: 'in 3-4 detailed paragraphs'
    }[options.maxLength || 'medium'];

    const focusInstruction = options.focusAreas?.length 
      ? `Focus particularly on: ${options.focusAreas.join(', ')}.` 
      : '';

    const prompt = `
Please provide a comprehensive summary of the following document ${lengthInstruction}.
${focusInstruction}
${options.includeKeyPoints ? 'Also extract key points as a separate list.' : ''}
Identify the main topics covered.

Return as JSON with summary, topics array${options.includeKeyPoints ? ', and keyPoints array' : ''}.

Document text:
${documentText}
    `;

    const messages: OpenAI.ChatCompletionMessageParam[] = [
      {
        role: "user",
        content: prompt,
      },
    ];

    const response = await this.chatCompletion(messages, {
      model: options.model || 'gpt-4o-mini',
      maxTokens: 2000,
    });

    try {
      const result = JSON.parse(response.content || '{}');
      return {
        summary: result.summary || '',
        keyPoints: options.includeKeyPoints ? result.keyPoints || [] : undefined,
        topics: result.topics || [],
      };
    } catch (error) {
      console.error('Failed to parse document summary:', error);
      return {
        summary: '',
        topics: [],
      };
    }
  }
}

// Export a default instance factory
export function createAIClient(config: AIClientConfig): AIClient {
  return new AIClient(config);
}

// Helper to create AI client from environment variables
export function createAIClientFromEnv(overrides: Partial<AIClientConfig> = {}): AIClient {
  const config: AIClientConfig = {
    apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY || process.env.OPENAI_API_KEY || '',
    baseURL: process.env.NEXT_PUBLIC_OPENAI_BASE_URL || process.env.OPENAI_BASE_URL,
    ...overrides,
  };

  if (!config.apiKey) {
    throw new Error(
      'OpenAI API key not found. Please set NEXT_PUBLIC_OPENAI_API_KEY or OPENAI_API_KEY environment variable.'
    );
  }

  return new AIClient(config);
}

// Example usage documentation
/*
Usage examples:

1. Basic usage with API key:
const client = createAIClient({ apiKey: 'your-api-key' });

2. Using environment variables:
const client = createAIClientFromEnv();

3. Describe an image:
const description = await client.describeImage(base64Image, {
  customPrompt: 'What mathematical equations are shown in this image?',
  detail: 'high'
});

4. Extract LaTeX:
const { latex, processedText } = await client.extractLatex(documentText, {
  includeInlineFormulas: true,
  preserveFormatting: true
});

5. Generate markdown table:
const table = await client.markdownTableFromMatrix(data, {
  includeHeaders: true,
  formatNumbers: true,
  alignment: ['left', 'center', 'right']
});

6. Streaming completion:
await client.streamChatCompletion(messages, {
  onChunk: (chunk) => console.log(chunk),
  onComplete: (fullText) => console.log('Complete:', fullText),
  onError: (error) => console.error('Error:', error)
});

7. Analyze document structure:
const analysis = await client.analyzeDocumentStructure(documentText, {
  extractTables: true,
  extractFormulas: true
});

8. Summarize document:
const summary = await client.summarizeDocument(documentText, {
  maxLength: 'medium',
  includeKeyPoints: true,
  focusAreas: ['methodology', 'results']
});
*/

// Export types for external use
export type { 
  AIClientConfig, 
  RateLimitConfig, 
  StreamingOptions, 
  MatrixData,
  ImageAnalysisOptions,
  LaTeXExtractionOptions,
  TableGenerationOptions
};
