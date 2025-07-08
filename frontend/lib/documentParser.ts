import mammoth from 'mammoth';
import * as XLSX from 'xlsx';
import { createWorker } from 'tesseract.js';
import { DocumentSection, ParsedDocument, DocumentMetadata, SupportedFileType } from '@/types/document';

export class DocumentParser {
  private static instance: DocumentParser;
  private ocrWorker: any = null;

  private constructor() {}

  public static getInstance(): DocumentParser {
    if (!DocumentParser.instance) {
      DocumentParser.instance = new DocumentParser();
    }
    return DocumentParser.instance;
  }

  public async parseDocument(
    file: File,
    onProgress?: (progress: number, message: string) => void
  ): Promise<ParsedDocument> {
    const fileType = this.getFileType(file);
    const metadata = this.createMetadata(file);
    
    onProgress?.(10, 'Starting document parsing...');

    let originalContent = '';
    let markdownContent = '';

    try {
      switch (fileType) {
        case 'txt':
          originalContent = await this.parseTxt(file);
          break;
        case 'docx':
          originalContent = await this.parseDocx(file, onProgress);
          break;
        case 'xlsx':
          originalContent = await this.parseXlsx(file, onProgress);
          break;
        case 'pdf':
          originalContent = await this.parsePdf(file, onProgress);
          break;
        case 'png':
        case 'jpg':
        case 'jpeg':
          originalContent = await this.parseImage(file, onProgress);
          break;
        default:
          throw new Error(`Unsupported file type: ${fileType}`);
      }

      onProgress?.(80, 'Converting to markdown...');
      markdownContent = this.convertToMarkdown(originalContent, fileType);
      
      onProgress?.(90, 'Extracting sections...');
      const sections = this.extractSections(markdownContent);

      onProgress?.(100, 'Parsing complete!');

      return {
        id: metadata.id,
        metadata,
        originalContent,
        markdownContent,
        sections
      };
    } catch (error) {
      throw new Error(`Failed to parse document: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private getFileType(file: File): SupportedFileType {
    const extension = file.name.split('.').pop()?.toLowerCase();
    const supportedTypes: SupportedFileType[] = ['pdf', 'docx', 'xlsx', 'ppt', 'txt', 'png', 'jpg', 'jpeg'];
    
    if (extension && supportedTypes.includes(extension as SupportedFileType)) {
      return extension as SupportedFileType;
    }
    
    throw new Error(`Unsupported file type: ${extension}`);
  }

  private createMetadata(file: File): DocumentMetadata {
    return {
      id: crypto.randomUUID(),
      name: file.name,
      type: file.type,
      size: file.size,
      uploadDate: new Date(),
      lastModified: new Date(file.lastModified)
    };
  }

  private async parseTxt(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = () => reject(new Error('Failed to read text file'));
      reader.readAsText(file);
    });
  }

  private async parseDocx(file: File, onProgress?: (progress: number, message: string) => void): Promise<string> {
    onProgress?.(30, 'Parsing DOCX file...');
    
    try {
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      
      if (result.messages.length > 0) {
        console.warn('DOCX parsing warnings:', result.messages);
      }
      
      return result.value;
    } catch (error) {
      throw new Error(`Failed to parse DOCX: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async parseXlsx(file: File, onProgress?: (progress: number, message: string) => void): Promise<string> {
    onProgress?.(30, 'Parsing Excel file...');
    
    try {
      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });
      
      let content = '';
      workbook.SheetNames.forEach((sheetName, index) => {
        const sheet = workbook.Sheets[sheetName];
        const sheetData = XLSX.utils.sheet_to_csv(sheet);
        content += `# Sheet: ${sheetName}\n\n${sheetData}\n\n`;
      });
      
      return content;
    } catch (error) {
      throw new Error(`Failed to parse Excel: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async parsePdf(file: File, onProgress?: (progress: number, message: string) => void): Promise<string> {
    onProgress?.(30, 'Parsing PDF file...');
    
    try {
      // For PDF parsing, we'll use a simple approach
      // In a real implementation, you might want to use pdf-parse or pdf.js
      const arrayBuffer = await file.arrayBuffer();
      // This is a placeholder - you'd need to implement actual PDF parsing
      return `PDF content from ${file.name} (${file.size} bytes)`;
    } catch (error) {
      throw new Error(`Failed to parse PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async parseImage(file: File, onProgress?: (progress: number, message: string) => void): Promise<string> {
    onProgress?.(30, 'Initializing OCR...');
    
    try {
      if (!this.ocrWorker) {
        this.ocrWorker = await createWorker();
        await this.ocrWorker.loadLanguage('eng');
        await this.ocrWorker.initialize('eng');
      }
      
      onProgress?.(50, 'Extracting text from image...');
      const { data: { text } } = await this.ocrWorker.recognize(file);
      
      return text;
    } catch (error) {
      throw new Error(`Failed to parse image: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private convertToMarkdown(content: string, fileType: SupportedFileType): string {
    switch (fileType) {
      case 'txt':
        return this.txtToMarkdown(content);
      case 'xlsx':
        return content; // Already formatted as markdown
      default:
        return this.genericToMarkdown(content);
    }
  }

  private txtToMarkdown(content: string): string {
    // Simple conversion for text files
    return content
      .split('\n\n')
      .map(paragraph => paragraph.trim())
      .filter(paragraph => paragraph.length > 0)
      .join('\n\n');
  }

  private genericToMarkdown(content: string): string {
    // Basic markdown conversion
    return content
      .replace(/^(.+)$/gm, '$1') // Basic paragraphs
      .replace(/\n\n+/g, '\n\n') // Clean up multiple newlines
      .trim();
  }

  private extractSections(markdown: string): DocumentSection[] {
    const sections: DocumentSection[] = [];
    const lines = markdown.split('\n');
    let currentSection: DocumentSection | null = null;
    let currentContent = '';
    let startIndex = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);

      if (headingMatch) {
        // Save previous section
        if (currentSection) {
          currentSection.content = currentContent.trim();
          currentSection.endIndex = startIndex + currentContent.length;
          sections.push(currentSection);
        }

        // Start new section
        const level = headingMatch[1].length;
        const title = headingMatch[2];
        startIndex = markdown.indexOf(line, startIndex);

        currentSection = {
          id: crypto.randomUUID(),
          title,
          content: '',
          startIndex,
          endIndex: 0,
          level
        };
        currentContent = '';
      } else {
        currentContent += line + '\n';
      }
    }

    // Save last section
    if (currentSection) {
      currentSection.content = currentContent.trim();
      currentSection.endIndex = startIndex + currentContent.length;
      sections.push(currentSection);
    }

    return sections;
  }

  public async cleanup(): Promise<void> {
    if (this.ocrWorker) {
      await this.ocrWorker.terminate();
      this.ocrWorker = null;
    }
  }
}