"""
User management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db


router = APIRouter()


@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db)):
    """
    Get all users.
    """
    return {"message": "List of users"}


@router.post("/")
async def create_user(db: AsyncSession = Depends(get_db)):
    """
    Create a new user.
    """
    return {"message": "User created"}
