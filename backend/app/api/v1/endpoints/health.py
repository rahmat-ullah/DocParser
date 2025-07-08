"""
Health check endpoints for monitoring backend status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db, check_db_connection
from app.services.ai_service import get_ai_service
from app.schemas.common import HealthCheck


router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def basic_health_check():
    """
    Basic health check endpoint.
    """
    return HealthCheck(
        status="healthy",
        service="document-parser-backend", 
        version="1.0.0"
    )


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check including database and AI service status.
    """
    # Check database connection
    db_healthy = await check_db_connection()
    
    # Check AI service
    ai_service = await get_ai_service()
    ai_status = await ai_service.health_check()
    
    return {
        "status": "healthy" if db_healthy and ai_status["status"] == "healthy" else "unhealthy",
        "service": "document-parser-backend",
        "version": "1.0.0",
        "components": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy"
            },
            "ai_service": ai_status
        }
    }
