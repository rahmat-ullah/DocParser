"""
File upload endpoints for document processing.
"""

import os
from typing import List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.document_service import DocumentService
from app.core.config import get_upload_config
from app.schemas.document import DocumentResponse, DocumentCreate


router = APIRouter()


@router.post("/", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file for processing.
    
    Args:
        file: The uploaded file
        user_id: Optional user ID
        db: Database session
        
    Returns:
        DocumentResponse with uploaded document details
    """
    upload_config = get_upload_config()
    
    # Validate file size
    if file.size > upload_config["max_size"]:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {upload_config['max_size']} bytes"
        )
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in upload_config["allowed_types"]:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {upload_config['allowed_types']}"
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Create document using service
    document_service = DocumentService(db)
    try:
        document = await document_service.create_document(
            filename=file.filename,
            file_content=file_content,
            file_type=file_ext,
            mime_type=file.content_type or "application/octet-stream",
            user_id=user_id
        )
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            file_type=document.file_type,
            mime_type=document.mime_type,
            processing_status=document.processing_status,
            created_at=document.created_at,
            user_id=document.user_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")


@router.post("/multiple", response_model=List[DocumentResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    user_id: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files for processing.
    
    Args:
        files: List of uploaded files
        user_id: Optional user ID
        db: Database session
        
    Returns:
        List of DocumentResponse with uploaded document details
    """
    upload_config = get_upload_config()
    
    if len(files) > upload_config["max_files"]:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum is {upload_config['max_files']} files per upload"
        )
    
    uploaded_documents = []
    document_service = DocumentService(db)
    
    for file in files:
        # Validate each file
        if file.size > upload_config["max_size"]:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} too large. Maximum size is {upload_config['max_size']} bytes"
            )
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in upload_config["allowed_types"]:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed for {file.filename}. Allowed types: {upload_config['allowed_types']}"
            )
    
    # Process all files
    for file in files:
        try:
            file_content = await file.read()
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            document = await document_service.create_document(
                filename=file.filename,
                file_content=file_content,
                file_type=file_ext,
                mime_type=file.content_type or "application/octet-stream",
                user_id=user_id
            )
            
            uploaded_documents.append(DocumentResponse(
                id=document.id,
                filename=document.filename,
                original_filename=document.original_filename,
                file_size=document.file_size,
                file_type=document.file_type,
                mime_type=document.mime_type,
                processing_status=document.processing_status,
                created_at=document.created_at,
                user_id=document.user_id
            ))
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process file {file.filename}: {str(e)}")
    
    return uploaded_documents
