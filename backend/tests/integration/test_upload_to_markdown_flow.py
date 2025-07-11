"""
Integration tests for the complete document upload to markdown save flow.
Tests the full pipeline from PDF upload to markdown file creation and retrieval.
"""

import pytest
import os
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock, Mock
import base64
import io

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.models.base import Base
from app.models.document import Document
from app.services.document_service import DocumentService
from app.services.document_processor import DocumentProcessor
from app.parsers.ast_models import DocumentAST, TextBlock, BlockType
from app.core.config import settings
from app.db.base import get_db


# Sample PDF data (minimal valid PDF)
SAMPLE_PDF_DATA = base64.b64encode(b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000229 00000 n 
0000000328 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
420
%%EOF""").decode()


@pytest.fixture
async def test_db():
    """Create a test database."""
    # Use SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()
    
    await engine.dispose()


@pytest.fixture
def override_db(test_db):
    """Override the database dependency."""
    async def _get_test_db():
        yield test_db
    
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_db):
    """Create test client with overridden dependencies."""
    return TestClient(app)


@pytest.fixture
def mock_ast():
    """Create a mock AST for testing."""
    return DocumentAST(
        metadata={
            "title": "Test PDF Document",
            "format": "pdf",
            "pages": 1
        },
        textBlocks=[
            TextBlock(
                content="Test PDF Content",
                type=BlockType.HEADING,
                level=1,
                page=1,
                bbox=[100, 700, 200, 720]
            ),
            TextBlock(
                content="This is a test PDF document for integration testing.",
                type=BlockType.PARAGRAPH,
                page=1,
                bbox=[100, 650, 400, 670]
            )
        ],
        images=[],
        tables=[],
        math=[]
    )


class TestUploadToMarkdownIntegration:
    """Integration tests for the complete upload to markdown flow."""
    
    @pytest.mark.asyncio
    async def test_full_pdf_upload_to_markdown_flow(self, client, test_db, mock_ast):
        """Test the complete flow from PDF upload to markdown file creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure temp directories
            upload_dir = Path(temp_dir) / "uploads"
            markdown_dir = Path(temp_dir) / "markdown"
            upload_dir.mkdir(parents=True, exist_ok=True)
            markdown_dir.mkdir(parents=True, exist_ok=True)
            
            with patch.object(settings, 'upload_dir', str(upload_dir)), \
                 patch.object(settings, 'markdown_dir', str(markdown_dir)):
                
                # Step 1: Upload PDF
                files = {
                    'file': ('test_document.pdf', base64.b64decode(SAMPLE_PDF_DATA.encode()), 'application/pdf')
                }
                
                upload_response = client.post("/api/v1/documents/upload", files=files)
                assert upload_response.status_code == 200
                
                upload_data = upload_response.json()
                document_id = upload_data["id"]
                assert upload_data["filename"] == "test_document.pdf"
                assert upload_data["mime_type"] == "application/pdf"
                
                # Verify document was saved to database
                doc_service = DocumentService(test_db)
                document = await doc_service.get_document(document_id)
                assert document is not None
                assert document.original_filename == "test_document.pdf"
                assert os.path.exists(document.file_path)
                
                # Step 2: Process document
                # Mock the parser to return our test AST
                with patch('app.parsers.parser_factory.ParserFactory.get_parser') as mock_get_parser:
                    mock_parser = Mock()
                    mock_parser.parse = AsyncMock(return_value=mock_ast)
                    mock_get_parser.return_value = mock_parser
                    
                    # Start processing
                    process_response = client.post(f"/api/v1/processing/{document_id}/process")
                    assert process_response.status_code == 200
                    
                    # Wait a bit for async processing
                    await asyncio.sleep(0.5)
                    
                    # Check processing status
                    status_response = client.get(f"/api/v1/processing/{document_id}/status")
                    assert status_response.status_code == 200
                    
                    # In a real scenario, we'd poll until completed
                    # For testing, we'll manually run the processor
                    processor = DocumentProcessor()
                    async for progress in processor.process_document(
                        Path(document.file_path),
                        document_id,
                        enable_ai_processing=False
                    ):
                        if progress.stage == "completion":
                            markdown_path = progress.details.get("markdown_path")
                            
                            # Update document with markdown path
                            await doc_service.update_document(
                                document_id,
                                {
                                    "processing_status": "completed",
                                    "markdown_path": markdown_path,
                                    "extracted_text": progress.result
                                }
                            )
                
                # Step 3: Verify markdown file was created
                expected_markdown_path = markdown_dir / document_id / "test_document.md"
                assert expected_markdown_path.exists()
                
                # Step 4: Check markdown content
                markdown_content = expected_markdown_path.read_text(encoding="utf-8")
                assert "# Test PDF Content" in markdown_content
                assert "This is a test PDF document for integration testing." in markdown_content
                assert "title: Test PDF Document" in markdown_content
                
                # Step 5: Test markdown download endpoint
                download_response = client.get(f"/api/v1/documents/{document_id}/markdown")
                assert download_response.status_code == 200
                assert download_response.headers["content-type"] == "text/markdown; charset=utf-8"
                assert b"# Test PDF Content" in download_response.content
    
    @pytest.mark.asyncio
    async def test_upload_process_multiple_documents(self, client, test_db, mock_ast):
        """Test uploading and processing multiple documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            upload_dir = Path(temp_dir) / "uploads"
            markdown_dir = Path(temp_dir) / "markdown"
            upload_dir.mkdir(parents=True, exist_ok=True)
            markdown_dir.mkdir(parents=True, exist_ok=True)
            
            with patch.object(settings, 'upload_dir', str(upload_dir)), \
                 patch.object(settings, 'markdown_dir', str(markdown_dir)), \
                 patch('app.parsers.parser_factory.ParserFactory.get_parser') as mock_get_parser:
                
                # Mock parser
                mock_parser = Mock()
                mock_parser.parse = AsyncMock(return_value=mock_ast)
                mock_get_parser.return_value = mock_parser
                
                document_ids = []
                
                # Upload multiple documents
                for i in range(3):
                    files = {
                        'file': (f'test_doc_{i}.pdf', base64.b64decode(SAMPLE_PDF_DATA.encode()), 'application/pdf')
                    }
                    
                    response = client.post("/api/v1/documents/upload", files=files)
                    assert response.status_code == 200
                    document_ids.append(response.json()["id"])
                
                # Process all documents
                processor = DocumentProcessor()
                for doc_id in document_ids:
                    doc_service = DocumentService(test_db)
                    document = await doc_service.get_document(doc_id)
                    
                    async for progress in processor.process_document(
                        Path(document.file_path),
                        doc_id,
                        enable_ai_processing=False
                    ):
                        if progress.stage == "completion":
                            await doc_service.update_document(
                                doc_id,
                                {
                                    "processing_status": "completed",
                                    "markdown_path": progress.details.get("markdown_path"),
                                    "extracted_text": progress.result
                                }
                            )
                
                # Verify all markdown files were created
                for i, doc_id in enumerate(document_ids):
                    expected_path = markdown_dir / doc_id / f"test_doc_{i}.md"
                    assert expected_path.exists()
                    
                    # Verify content
                    content = expected_path.read_text(encoding="utf-8")
                    assert "# Test PDF Content" in content
    
    @pytest.mark.asyncio
    async def test_markdown_path_persistence_in_db(self, client, test_db):
        """Test that markdown_path is correctly saved and retrieved from database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test document
            doc_service = DocumentService(test_db)
            
            # Create document
            document = await doc_service.create_document(
                filename="test_file.pdf",
                original_filename="Test File.pdf",
                file_size=1024,
                file_type=".pdf",
                mime_type="application/pdf",
                file_path=os.path.join(temp_dir, "test_file.pdf"),
                user_id="test_user"
            )
            
            # Update with markdown path
            markdown_path = os.path.join(temp_dir, "markdown", document.id, "test_file.md")
            updated_doc = await doc_service.update_markdown_path(document.id, markdown_path)
            
            assert updated_doc.markdown_path == markdown_path
            
            # Retrieve and verify
            retrieved_doc = await doc_service.get_document(document.id)
            assert retrieved_doc.markdown_path == markdown_path
            
            # Test the get_markdown_path method
            path_from_service = await doc_service.get_markdown_path(document.id)
            assert path_from_service == markdown_path
    
    @pytest.mark.asyncio
    async def test_error_handling_during_processing(self, client, test_db):
        """Test error handling when processing fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            upload_dir = Path(temp_dir) / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            with patch.object(settings, 'upload_dir', str(upload_dir)):
                # Upload a file
                files = {
                    'file': ('test.pdf', b'invalid pdf data', 'application/pdf')
                }
                
                upload_response = client.post("/api/v1/documents/upload", files=files)
                assert upload_response.status_code == 200
                document_id = upload_response.json()["id"]
                
                # Mock parser to raise an exception
                with patch('app.parsers.parser_factory.ParserFactory.get_parser') as mock_get_parser:
                    mock_parser = Mock()
                    mock_parser.parse = AsyncMock(side_effect=Exception("Parsing failed"))
                    mock_get_parser.return_value = mock_parser
                    
                    # Try to process
                    processor = DocumentProcessor()
                    doc_service = DocumentService(test_db)
                    document = await doc_service.get_document(document_id)
                    
                    error_found = False
                    async for progress in processor.process_document(
                        Path(document.file_path),
                        document_id,
                        enable_ai_processing=False
                    ):
                        if progress.stage == "error":
                            error_found = True
                            assert "Parsing failed" in progress.message
                    
                    assert error_found, "Expected error progress but none found"
