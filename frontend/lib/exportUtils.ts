import { saveAs } from 'file-saver';
import { ParsedDocument } from '@/types/document';

export class ExportManager {
  public static exportAsMarkdown(document: ParsedDocument): void {
    const content = this.formatMarkdownForExport(document);
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const filename = `${document.metadata.name.replace(/\.[^/.]+$/, '')}.md`;
    saveAs(blob, filename);
  }

  public static exportAsJSON(document: ParsedDocument): void {
    const jsonData = {
      metadata: document.metadata,
      content: document.markdownContent,
      sections: document.sections,
      exportDate: new Date().toISOString()
    };
    
    const content = JSON.stringify(jsonData, null, 2);
    const blob = new Blob([content], { type: 'application/json;charset=utf-8' });
    const filename = `${document.metadata.name.replace(/\.[^/.]+$/, '')}.json`;
    saveAs(blob, filename);
  }

  public static exportMultipleAsZip(documents: ParsedDocument[]): void {
    // This would require a zip library like JSZip
    // For now, we'll export them individually
    documents.forEach(doc => {
      this.exportAsMarkdown(doc);
    });
  }

  private static formatMarkdownForExport(document: ParsedDocument): string {
    const header = `---
title: ${document.metadata.name}
type: ${document.metadata.type}
size: ${document.metadata.size}
uploaded: ${document.metadata.uploadDate.toISOString()}
exported: ${new Date().toISOString()}
---

`;
    
    return header + document.markdownContent;
  }
}