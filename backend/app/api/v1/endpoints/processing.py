"""
Document processing endpoints for AI analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db


router = APIRouter()


@router.post("/{document_id}")
async def process_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """
    Process a document with AI analysis.
    """
    return {"message": f"Processing document {document_id}"}
