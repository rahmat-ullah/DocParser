"""
Common schemas for API metadata and pagination.
"""

from typing import Optional, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """
    Schema for health check response.
    """
    status: str = Field(..., example="healthy")
    service: str = Field(..., example="document-parser-backend")
    version: str = Field(..., example="1.0.0")


class APIResponse(BaseModel):
    """
    General schema for API responses.
    """
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class PaginationParams(BaseModel):
    """
    Schema for pagination parameters.
    """
    page: Optional[int] = Field(1, gt=0)
    limit: Optional[int] = Field(10, gt=0, le=100)


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Schema for paginated API responses.
    """
    total: int
    page: int
    limit: int
    items: List[T]


__all__ = ["HealthCheck", "APIResponse", "PaginationParams", "PaginatedResponse"]
