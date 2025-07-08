"""
File upload endpoints for document processing.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db


router = APIRouter()


@router.post("/")
async def upload_file(db: AsyncSession = Depends(get_db)):
    """
    Upload a file for processing.
    """
    return {"message": "File uploaded successfully"}
