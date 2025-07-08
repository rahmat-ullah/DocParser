"""
Endpoints for document management and retrieval.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
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
