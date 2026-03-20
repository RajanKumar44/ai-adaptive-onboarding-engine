"""
Pagination Models and Utilities

Provides pagination support for list endpoints with:
- Standard pagination parameters
- Paginated response wrapper
- Default pagination settings
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, TypeVar, Generic, Optional, Any, Literal
from math import ceil
from enum import Enum

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of items to return (max 100)"
    )
    
    def get_offset(self) -> int:
        """Get offset for database query"""
        return self.skip
    
    def get_limit(self) -> int:
        """Get limit for database query"""
        return self.limit


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class SortParam(BaseModel):
    """Sort parameter"""
    
    model_config = ConfigDict(use_enum_values=True)
    
    field: str = Field(description="Field name to sort by")
    order: SortOrder = Field(default=SortOrder.ASC, description="Sort order (asc or desc)")


class FilterParam(BaseModel):
    """Filter parameter"""
    
    field: str = Field(description="Field name to filter")
    operator: str = Field(description="Filter operator (eq, ne, gt, gte, lt, lte, like, in)")
    value: Any = Field(description="Filter value")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper"""
    
    data: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items (before pagination)")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items returned")
    page: int = Field(description="Current page number (1-indexed)")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        skip: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response"""
        page = (skip // limit) + 1 if limit > 0 else 1
        pages = ceil(total / limit) if limit > 0 else 0
        
        return cls(
            data=data,
            total=total,
            skip=skip,
            limit=limit,
            page=page,
            pages=pages,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )


class CursorPaginationParams(BaseModel):
    """Cursor-based pagination parameters (more efficient for large datasets)"""
    
    cursor: Optional[str] = Field(default=None, description="Cursor from previous response")
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of items to return"
    )


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response"""
    
    data: List[T] = Field(description="List of items")
    cursor: Optional[str] = Field(description="Cursor for next page (null if end of results)")
    limit: int = Field(description="Number of items returned")
    has_next: bool = Field(description="Whether there is a next page")
    
    @classmethod
    def create(
        cls,
        data: List[T],
        cursor: Optional[str] = None,
        limit: int = 10
    ) -> "CursorPaginatedResponse[T]":
        """Create a cursor-paginated response"""
        return cls(
            data=data,
            cursor=cursor,
            limit=limit,
            has_next=cursor is not None
        )


# Pagination presets for different entity t types
class PaginationPresets:
    """Standard pagination presets"""
    
    # Small lists (users, roles, etc)
    SMALL = {"default_limit": 10, "max_limit": 50}
    
    # Medium lists (analyses, results)
    MEDIUM = {"default_limit": 25, "max_limit": 100}
    
    # Large lists (logs, events)
    LARGE = {"default_limit": 50, "max_limit": 500}
    
    # Very large lists (audit logs)
    VERY_LARGE = {"default_limit": 100, "max_limit": 1000}
    
    @classmethod
    def apply_limit(cls, limit: int, preset: dict) -> int:
        """Apply preset constraints to limit"""
        return min(
            max(1, limit),
            preset.get("max_limit", 100)
        )
