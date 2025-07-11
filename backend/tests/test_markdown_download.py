"""
Unit tests for markdown download endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import os
import tempfile

from app.main import app
from app.models.document import Document
from app.services.document_service import DocumentService


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_document():
    """Create a mock document."""
    return Document(
        id="test-123",
        filename="test.pdf",
        original_filename="Test Document.pdf",
        file_size=1024,
        file_type=".pdf",
        mime_type="application/pdf",
        file_path="/tmp/test.pdf",
        processing_status="completed",
        markdown_path="/tmp/test_123.md",
        extracted_text="# Test Document\n\nThis is test content."
    )


class TestMarkdownDownload:
    """Test cases for markdown download endpoint."""
    
    @pytest.mark.asyncio
    async def test_download_markdown_success(self, client, mock_document):
        """Test successful markdown download."""
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Markdown\n\nContent here.")
            temp_path = f.name
        
        try:
            mock_document.markdown_path = temp_path
            
            with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
                response = client.get(f"/api/v1/documents/{mock_document.id}/markdown")
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/markdown; charset=utf-8"
                assert "attachment" in response.headers["content-disposition"]
                assert "Test Document.md" in response.headers["content-disposition"]
                assert response.content == b"# Test Markdown\n\nContent here."
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_download_markdown_not_found(self, client):
        """Test download with non-existent document."""
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=None)):
            response = client.get("/api/v1/documents/non-existent/markdown")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Document not found"
    
    @pytest.mark.asyncio
    async def test_download_markdown_processing_incomplete(self, client, mock_document):
        """Test download with incomplete processing."""
        mock_document.processing_status = "processing"
        
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
            response = client.get(f"/api/v1/documents/{mock_document.id}/markdown")
            
            assert response.status_code == 409
            assert "processing not completed" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_download_markdown_no_path(self, client, mock_document):
        """Test download when markdown_path is not set."""
        mock_document.markdown_path = None
        
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
            response = client.get(f"/api/v1/documents/{mock_document.id}/markdown")
            
            assert response.status_code == 409
            assert "not been generated" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_download_markdown_file_missing(self, client, mock_document):
        """Test download when file doesn't exist on disk."""
        mock_document.markdown_path = "/non/existent/file.md"
        
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
            response = client.get(f"/api/v1/documents/{mock_document.id}/markdown")
            
            assert response.status_code == 409
            assert "file not found on disk" in response.json()["detail"]


class TestExportEndpoints:
    """Test cases for export endpoints."""
    
    @pytest.mark.asyncio
    async def test_export_markdown_cached(self, client, mock_document):
        """Test export with cached markdown option."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Cached Markdown")
            temp_path = f.name
        
        try:
            mock_document.markdown_path = temp_path
            
            with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
                response = client.post(
                    f"/api/v1/export/{mock_document.id}",
                    json={
                        "format": "markdown",
                        "options": {"cached": True}
                    }
                )
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_export_unsupported_format(self, client, mock_document):
        """Test export with unsupported format."""
        with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
            response = client.post(
                f"/api/v1/export/{mock_document.id}",
                json={"format": "invalid"}
            )
            
            assert response.status_code == 400
            assert "Unsupported export format" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_available_formats(self, client, mock_document):
        """Test getting available export formats."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            mock_document.markdown_path = temp_path
            
            with patch.object(DocumentService, 'get_document', new=AsyncMock(return_value=mock_document)):
                response = client.get(f"/api/v1/export/{mock_document.id}/formats")
                
                assert response.status_code == 200
                data = response.json()
                assert data["document_id"] == mock_document.id
                assert data["processing_status"] == "completed"
                assert len(data["available_formats"]) > 0
                
                # Check that cached markdown is available
                cached_markdown = next(
                    (f for f in data["available_formats"] 
                     if f["format"] == "markdown" and f["cached"]), 
                    None
                )
                assert cached_markdown is not None
        finally:
            os.unlink(temp_path)
