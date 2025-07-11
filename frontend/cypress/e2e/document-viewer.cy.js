/// <reference types="cypress" />

describe('Document Viewer - PDF and Markdown Panes', () => {
  const testDocumentId = 'test-doc-123';
  
  beforeEach(() => {
    // Visit the home page
    cy.visit('/');
  });

  it('should display both PDF and Markdown panes after processing', () => {
    // Mock the document data
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}`, {
      statusCode: 200,
      body: {
        id: testDocumentId,
        filename: 'test-document.pdf',
        original_filename: 'Test Document.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        processing_status: 'completed',
        file_path: '/uploads/test-document.pdf',
        extracted_text: '# Test Document\n\nThis is the extracted content.',
        markdown_path: '/markdown/test-doc-123/test-document.md'
      }
    }).as('getDocument');

    // Mock the processing status as completed
    cy.mockProcessingStatus(testDocumentId, 'completed');

    // Mock the PDF file endpoint
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}/file`, {
      statusCode: 200,
      headers: {
        'content-type': 'application/pdf',
        'content-disposition': 'inline; filename="test-document.pdf"'
      },
      body: 'PDF_BINARY_DATA_HERE'
    }).as('getPdfFile');

    // Mock the markdown download endpoint
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}/markdown`, {
      statusCode: 200,
      headers: {
        'content-type': 'text/markdown; charset=utf-8'
      },
      body: '# Test Document\n\nThis is the markdown content.\n\n## Section 1\n\nSome content here.'
    }).as('getMarkdown');

    // Navigate to the document viewer
    cy.visit(`/documents/${testDocumentId}`);
    
    // Wait for the document data to load
    cy.wait('@getDocument');
    cy.wait('@processingStatus');

    // Verify both panes are visible
    cy.get('[data-testid="pdf-viewer-pane"]', { timeout: 10000 }).should('be.visible');
    cy.get('[data-testid="markdown-viewer-pane"]', { timeout: 10000 }).should('be.visible');

    // Verify PDF viewer contains iframe or embed element
    cy.get('[data-testid="pdf-viewer-pane"]').within(() => {
      cy.get('iframe, embed, object').should('exist').and('be.visible');
    });

    // Verify Markdown content is displayed
    cy.get('[data-testid="markdown-viewer-pane"]').within(() => {
      cy.contains('h1', 'Test Document').should('be.visible');
      cy.contains('h2', 'Section 1').should('be.visible');
    });

    // Verify download button exists and works
    cy.get('[data-testid="download-markdown-btn"]').should('be.visible').click();
    cy.wait('@getMarkdown').then((interception) => {
      expect(interception.response.statusCode).to.equal(200);
    });
  });

  it('should show loading state while processing', () => {
    // Mock document as processing
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}`, {
      statusCode: 200,
      body: {
        id: testDocumentId,
        filename: 'test-document.pdf',
        processing_status: 'processing'
      }
    }).as('getProcessingDocument');

    cy.mockProcessingStatus(testDocumentId, 'processing');

    // Navigate to document
    cy.visit(`/documents/${testDocumentId}`);
    cy.wait('@getProcessingDocument');

    // Should show processing indicator
    cy.get('[data-testid="processing-indicator"]').should('be.visible');
    cy.contains(/processing|analyzing/i).should('be.visible');

    // PDF and Markdown panes should not be visible yet
    cy.get('[data-testid="pdf-viewer-pane"]').should('not.exist');
    cy.get('[data-testid="markdown-viewer-pane"]').should('not.exist');
  });

  it('should handle document upload and processing flow', () => {
    // Mock file upload
    cy.mockDocumentUpload();

    // Mock processing start
    cy.intercept('POST', `**/api/v1/processing/test-doc-123/process`, {
      statusCode: 200,
      body: {
        message: 'Processing started',
        document_id: 'test-doc-123'
      }
    }).as('startProcessing');

    // Upload a file
    cy.get('[data-testid="file-upload-dropzone"]').should('be.visible');
    
    // Create a test PDF file fixture if it doesn't exist
    const pdfContent = btoa('%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj');
    cy.writeFile('cypress/fixtures/test-document.pdf', pdfContent, 'base64');
    
    // Upload the file
    cy.uploadFile('test-document.pdf');
    cy.wait('@documentUpload');

    // Should redirect to document page
    cy.url().should('include', '/documents/test-doc-123');

    // Mock completed status for next check
    cy.mockProcessingStatus('test-doc-123', 'completed');
    
    // Mock the document data as completed
    cy.intercept('GET', '**/api/v1/documents/test-doc-123', {
      statusCode: 200,
      body: {
        id: 'test-doc-123',
        filename: 'test-document.pdf',
        processing_status: 'completed',
        extracted_text: '# Processed Document\n\nContent extracted successfully.'
      }
    }).as('getCompletedDocument');

    // Wait for processing to complete
    cy.wait(2000); // Simulate processing time
    cy.reload(); // Reload to get updated status

    // Both panes should now be visible
    cy.get('[data-testid="pdf-viewer-pane"]', { timeout: 15000 }).should('be.visible');
    cy.get('[data-testid="markdown-viewer-pane"]', { timeout: 15000 }).should('be.visible');
  });

  it('should maintain split pane functionality', () => {
    // Set up completed document
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}`, {
      statusCode: 200,
      body: {
        id: testDocumentId,
        filename: 'test-document.pdf',
        processing_status: 'completed',
        extracted_text: '# Test Document'
      }
    }).as('getDocument');

    cy.mockProcessingStatus(testDocumentId, 'completed');

    cy.visit(`/documents/${testDocumentId}`);
    cy.wait('@getDocument');

    // Check for split pane divider
    cy.get('[data-testid="split-pane-divider"]').should('be.visible');

    // Test resizing functionality (if implemented)
    cy.get('[data-testid="split-pane-divider"]')
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 400 })
      .trigger('mouseup');

    // Both panes should still be visible after resize
    cy.get('[data-testid="pdf-viewer-pane"]').should('be.visible');
    cy.get('[data-testid="markdown-viewer-pane"]').should('be.visible');
  });

  it('should verify download link returns 200', () => {
    // Set up completed document
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}`, {
      statusCode: 200,
      body: {
        id: testDocumentId,
        processing_status: 'completed',
        markdown_path: '/markdown/test-doc-123/test-document.md'
      }
    }).as('getDocument');

    cy.visit(`/documents/${testDocumentId}`);
    cy.wait('@getDocument');

    // Verify markdown download returns 200
    cy.verifyMarkdownDownload(testDocumentId);
  });

  it('should handle missing PDF gracefully', () => {
    // Mock document without PDF file
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}`, {
      statusCode: 200,
      body: {
        id: testDocumentId,
        filename: 'test-document.pdf',
        processing_status: 'completed',
        extracted_text: '# Document processed\n\nPDF file not available.'
      }
    }).as('getDocument');

    // Mock 404 for PDF file
    cy.intercept('GET', `**/api/v1/documents/${testDocumentId}/file`, {
      statusCode: 404,
      body: { detail: 'File not found' }
    }).as('getPdfFile404');

    cy.visit(`/documents/${testDocumentId}`);
    cy.wait('@getDocument');

    // Should show error message in PDF pane
    cy.get('[data-testid="pdf-viewer-pane"]').within(() => {
      cy.contains(/unable to load|not available|error/i).should('be.visible');
    });

    // Markdown pane should still work
    cy.get('[data-testid="markdown-viewer-pane"]').should('be.visible');
  });
});
