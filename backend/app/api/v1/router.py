"""
Main API router for v1 endpoints.
Combines all API route modules.
"""

from fastapi import APIRouter

from .endpoints import documents, health, upload, processing, users, export, image_metadata


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(image_metadata.router, prefix="/images", tags=["images"])
