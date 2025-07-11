// ***********************************************
// Custom commands for document processing tests
// ***********************************************

// Upload a file through the UI
Cypress.Commands.add('uploadFile', (fileName, mimeType = 'application/pdf') => {
  cy.fixture(fileName, 'base64').then(fileContent => {
    const blob = Cypress.Blob.base64StringToBlob(fileContent, mimeType);
    const file = new File([blob], fileName, { type: mimeType });
    
    cy.get('input[type="file"]').then(input => {
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      input[0].files = dataTransfer.files;
      
      // Trigger change event
      cy.wrap(input).trigger('change', { force: true });
    });
  });
});

// Wait for document processing to complete
Cypress.Commands.add('waitForProcessing', (documentId, timeout = 30000) => {
  cy.intercept('GET', `**/api/v1/processing/${documentId}/status`).as('checkStatus');
  
  const checkStatus = () => {
    cy.wait('@checkStatus', { timeout: 5000 }).then(interception => {
      const status = interception.response.body.status;
      
      if (status === 'completed') {
        return;
      } else if (status === 'failed') {
        throw new Error('Document processing failed');
      } else {
        // Continue polling
        cy.wait(1000);
        cy.visit(`/documents/${documentId}`, { timeout: 1000 });
        checkStatus();
      }
    });
  };
  
  checkStatus();
});

// Check if markdown download link works
Cypress.Commands.add('verifyMarkdownDownload', (documentId) => {
  cy.request({
    url: `${Cypress.env('apiUrl')}/documents/${documentId}/markdown`,
    method: 'GET',
    failOnStatusCode: false
  }).then(response => {
    expect(response.status).to.eq(200);
    expect(response.headers['content-type']).to.include('text/markdown');
    expect(response.body).to.include('#'); // Should contain at least one heading
  });
});

// Mock successful document upload
Cypress.Commands.add('mockDocumentUpload', () => {
  cy.intercept('POST', '**/api/v1/documents/upload', {
    statusCode: 200,
    body: {
      id: 'test-doc-123',
      filename: 'test-document.pdf',
      original_filename: 'Test Document.pdf',
      file_size: 1024,
      mime_type: 'application/pdf',
      upload_timestamp: new Date().toISOString(),
      processing_status: 'pending'
    }
  }).as('documentUpload');
});

// Mock document processing status
Cypress.Commands.add('mockProcessingStatus', (documentId, status = 'completed') => {
  const baseResponse = {
    document_id: documentId,
    status: status,
    started_at: new Date(Date.now() - 10000).toISOString(),
    markdown_url: `${Cypress.env('apiUrl')}/documents/${documentId}/markdown`
  };
  
  if (status === 'completed') {
    baseResponse.completed_at = new Date().toISOString();
    baseResponse.result = '# Test Document\n\nThis is the processed content.';
  } else if (status === 'failed') {
    baseResponse.completed_at = new Date().toISOString();
    baseResponse.error = 'Processing failed due to invalid format';
  }
  
  cy.intercept('GET', `**/api/v1/processing/${documentId}/status`, {
    statusCode: 200,
    body: baseResponse
  }).as('processingStatus');
});
