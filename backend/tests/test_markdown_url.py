"""
Test markdown_url field in status and result endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.main import app
from app.services.document_service import DocumentService
from app.models.document import Document


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestMarkdownURL:
    """Test markdown_url is properly included in responses."""
    
    @pytest.fixture
    def mock_document(self):
        """Create a mock document."""
        return Document(
            id="test-123",
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size=1000,
            file_type=".pdf",
            mime_type="application/pdf",
            processing_status="completed",
            extracted_text="Test content",
            ai_description="Test AI description",
            processing_started_at=datetime.now(),
            processing_completed_at=datetime.now(),
            markdown_path="/markdown/test.md"
        )
    
    @pytest.mark.asyncio
    async def test_status_endpoint_includes_markdown_url(self, client, mock_document):
        """Test that status endpoint includes markdown_url."""
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
            response = client.get(f"/api/v1/processing/{mock_document.id}/status")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all expected fields
            assert "document_id" in data
            assert "status" in data
            assert "markdown_url" in data
            
            # Verify markdown_url format
            assert data["markdown_url"].endswith(f"/api/v1/documents/{mock_document.id}/markdown")
            assert data["document_id"] == mock_document.id
            assert data["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_result_endpoint_includes_markdown_url(self, client, mock_document):
        """Test that result endpoint includes markdown_url."""
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
            response = client.get(f"/api/v1/processing/{mock_document.id}/result")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all expected fields
            assert "document_id" in data
            assert "extracted_text" in data
            assert "ai_description" in data
            assert "completed_at" in data
            assert "markdown_url" in data
            
            # Verify markdown_url format
            assert data["markdown_url"].endswith(f"/api/v1/documents/{mock_document.id}/markdown")
            assert data["document_id"] == mock_document.id
            assert data["extracted_text"] == "Test content"
            assert data["ai_description"] == "Test AI description"
    
    @pytest.mark.asyncio
    async def test_status_endpoint_markdown_url_for_incomplete_document(self, client):
        """Test that markdown_url is still included even for incomplete documents."""
        mock_doc = Document(
            id="test-456",
            filename="incomplete.pdf",
            original_filename="incomplete.pdf",
            file_path="/uploads/incomplete.pdf",
            file_size=1000,
            file_type=".pdf",
            mime_type="application/pdf",
            processing_status="processing",
            processing_started_at=datetime.now()
        )
        
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_doc)):
            response = client.get(f"/api/v1/processing/{mock_doc.id}/status")
            
            assert response.status_code == 200
            data = response.json()
            
            # markdown_url should still be present even if document is not completed
            assert "markdown_url" in data
            assert data["markdown_url"].endswith(f"/api/v1/documents/{mock_doc.id}/markdown")
            assert data["status"] == "processing"
            assert data["result"] is None  # No result for incomplete document
