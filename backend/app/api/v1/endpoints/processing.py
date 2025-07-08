"""
Document processing endpoints for AI analysis.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.services.document_service import DocumentService
from app.services.document_processor import DocumentProcessor
from app.schemas.document import DocumentResponse
from pathlib import Path


router = APIRouter()


class ProcessingRequest(BaseModel):
    """Request model for document processing."""
    enable_ai_processing: bool = True
    processing_options: Optional[Dict[str, Any]] = None


class ProcessingResponse(BaseModel):
    """Response model for document processing."""
    message: str
    document_id: str
    status: str


@router.post("/{document_id}", response_model=ProcessingResponse)
async def process_document(
    document_id: str, 
    request: ProcessingRequest = ProcessingRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db)
):
    """
    Process a document with AI analysis.
    
    Args:
        document_id: ID of the document to process
        request: Processing configuration
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        ProcessingResponse indicating processing has started
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.processing_status == "processing":
        raise HTTPException(status_code=400, detail="Document is already being processed")
    
    # Start processing in background
    background_tasks.add_task(
        _process_document_background,
        document_id,
        request.enable_ai_processing,
        request.processing_options or {},
        db
    )
    
    # Update status immediately
    await document_service.update_document(
        document_id,
        {"processing_status": "processing"}
    )
    
    return ProcessingResponse(
        message="Document processing started",
        document_id=document_id,
        status="processing"
    )


@router.get("/{document_id}/status")
async def get_processing_status(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing status of a document.
    
    Args:
        document_id: ID of the document
        db: Database session
        
    Returns:
        Processing status information
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "status": document.processing_status,
        "started_at": document.processing_started_at,
        "completed_at": document.processing_completed_at,
        "error": document.processing_error,
        "result": document.extracted_text if document.processing_status == "completed" else None
    }


@router.get("/{document_id}/result")
async def get_processing_result(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing result of a completed document.
    
    Args:
        document_id: ID of the document
        db: Database session
        
    Returns:
        Processing result content
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Document processing not completed. Status: {document.processing_status}"
        )
    
    return {
        "document_id": document_id,
        "extracted_text": document.extracted_text,
        "ai_description": document.ai_description,
        "completed_at": document.processing_completed_at
    }


async def _process_document_background(
    document_id: str,
    enable_ai_processing: bool,
    processing_options: Dict[str, Any],
    db: AsyncSession
):
    """
    Background task for processing documents.
    
    Args:
        document_id: ID of the document to process
        enable_ai_processing: Whether to enable AI processing
        processing_options: Processing configuration
        db: Database session
    """
    document_service = DocumentService(db)
    document_processor = DocumentProcessor()
    
    try:
        document = await document_service.get_document(document_id)
        if not document:
            return
        
        file_path = Path(document.file_path)
        
        # Process the document
        markdown_content = ""
        async for progress in document_processor.process_document(
            file_path, 
            document_id, 
            enable_ai_processing
        ):
            if progress.stage == "completion" and hasattr(progress, 'result'):
                markdown_content = progress.result
        
        # Update document with results
        await document_service.update_document(
            document_id,
            {
                "processing_status": "completed",
                "extracted_text": markdown_content,
                "ai_description": f"Document processed successfully with AI={enable_ai_processing}"
            }
        )
        
    except Exception as e:
        # Update document with error
        await document_service.update_document(
            document_id,
            {
                "processing_status": "failed",
                "processing_error": str(e)
            }
        )
