"""
Endpoints for document management and retrieval.
"""

from typing import List
import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import DocumentService
from app.schemas.document import DocumentResponse


router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all documents.
    """
    document_service = DocumentService(db)
    documents = await document_service.list_documents()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single document by ID.
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a document by ID.
    """
    document_service = DocumentService(db)
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}


@router.get("/{document_id}/file")
async def get_document_file(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get the original PDF file for a document.
    
    Returns:
        FileResponse: The PDF file displayed inline
    
    Raises:
        404: Document not found or file not found
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if file_path exists
    if not document.file_path:
        raise HTTPException(
            status_code=404,
            detail="File path not found for this document"
        )
    
    # Check if the file exists on disk
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found on disk"
        )
    
    return FileResponse(
        path=document.file_path,
        media_type=document.mime_type or "application/pdf",
        filename=document.original_filename,
        headers={
            "Content-Disposition": f'inline; filename="{document.original_filename}"'
        }
    )


@router.get("/{document_id}/markdown")
async def download_markdown(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Download the saved Markdown file for a document.
    
    Returns:
        FileResponse: The Markdown file as an attachment
    
    Raises:
        404: Document not found
        409: Document processing not completed or markdown file not generated
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if processing is completed
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=409, 
            detail=f"Document processing not completed. Current status: {document.processing_status}"
        )
    
    # Check if markdown_path exists
    if not document.markdown_path:
        raise HTTPException(
            status_code=409,
            detail="Markdown file has not been generated for this document"
        )
    
    # Check if the file exists on disk
    if not os.path.exists(document.markdown_path):
        raise HTTPException(
            status_code=409,
            detail="Markdown file path exists in database but file not found on disk"
        )
    
    # Prepare filename for download
    download_filename = f"{os.path.splitext(document.original_filename)[0]}.md"
    
    return FileResponse(
        path=document.markdown_path,
        media_type="text/markdown",
        filename=download_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{download_filename}"'
        }
    )
