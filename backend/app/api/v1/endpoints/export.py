"""
Export endpoints for document conversion and download.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import os

from app.db.database import get_db
from app.services.document_service import DocumentService
from app.api.v1.endpoints.documents import download_markdown


class ExportOptions(BaseModel):
    """Options for document export."""
    cached: bool = False
    include_metadata: bool = True


class ExportRequest(BaseModel):
    """Request model for document export."""
    format: str  # markdown, pdf, docx, etc.
    options: Optional[ExportOptions] = ExportOptions()


router = APIRouter()


@router.post("/{document_id}")
async def export_document(
    document_id: str,
    export_request: ExportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Export a document in the specified format.
    
    Args:
        document_id: ID of the document to export
        export_request: Export format and options
        db: Database session
        
    Returns:
        FileResponse with the exported document
        
    Raises:
        404: Document not found
        409: Document processing not completed
        400: Invalid format or export options
    """
    # For markdown format with cached option, reuse the download_markdown endpoint
    if export_request.format.lower() == "markdown" and export_request.options.cached:
        return await download_markdown(document_id, db)
    
    # Get document
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
    
    # Handle other export formats
    if export_request.format.lower() == "markdown" and not export_request.options.cached:
        # Generate markdown on-the-fly (not from cached file)
        # This would involve regenerating the markdown from the extracted text
        raise HTTPException(
            status_code=501,
            detail="On-the-fly markdown generation not yet implemented"
        )
    elif export_request.format.lower() in ["pdf", "docx", "html"]:
        raise HTTPException(
            status_code=501,
            detail=f"Export to {export_request.format} format not yet implemented"
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format: {export_request.format}"
        )


@router.get("/{document_id}/formats")
async def get_available_formats(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get available export formats for a document.
    
    Args:
        document_id: ID of the document
        db: Database session
        
    Returns:
        List of available export formats
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    available_formats = []
    
    # Check if cached markdown is available
    if document.markdown_path and os.path.exists(document.markdown_path):
        available_formats.append({
            "format": "markdown",
            "cached": True,
            "description": "Cached markdown file"
        })
    
    # Always available if document is processed
    if document.processing_status == "completed":
        available_formats.extend([
            {
                "format": "markdown",
                "cached": False,
                "description": "Generate markdown on-the-fly"
            },
            {
                "format": "pdf",
                "cached": False,
                "description": "Export as PDF (not yet implemented)"
            },
            {
                "format": "docx",
                "cached": False,
                "description": "Export as Word document (not yet implemented)"
            },
            {
                "format": "html",
                "cached": False,
                "description": "Export as HTML (not yet implemented)"
            }
        ])
    
    return {
        "document_id": document_id,
        "processing_status": document.processing_status,
        "available_formats": available_formats
    }
