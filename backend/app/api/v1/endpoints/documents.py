"""
Endpoints for document management and retrieval.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db


router = APIRouter()


@router.get("/")
async def get_documents(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all documents.
    """
    return {"message": "List of documents"}


@router.post("/")
async def create_document(db: AsyncSession = Depends(get_db)):
    """
    Create a new document.
    """
    return {"message": "Document created"}
