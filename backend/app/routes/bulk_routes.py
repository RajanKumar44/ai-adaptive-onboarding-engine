"""
Bulk Operations Routes

Provides endpoints for bulk create, update, and delete operations on:
- Users
- Analyses

Supports atomic and partial failure modes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.analysis import Analysis
from app.core.bulk_operations import (
    BulkOperationHandler,
    BulkOperationRequest,
    BulkOperationResult,
    BulkOperationType
)
from app.schemas.auth_schema import UserResponse
from app.middleware.rate_limiting import RateLimits, limiter

router = APIRouter(prefix="/api/v1/bulk", tags=["bulk-operations"])

# Initialize bulk handler
bulk_handler = BulkOperationHandler(batch_size=100)


@router.post("/users/create", response_model=BulkOperationResult, status_code=201)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_create_users(
    request: BulkOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk create multiple users.
    
    Admin-only operation.
    
    Args:
        request: Bulk operation request with list of user data
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        BulkOperationResult with status of each created user
        
    Raises:
        HTTPException: If not authorized or operation type mismatch
        
    Example:
        {
            "operation": "create",
            "items": [
                {"email": "user1@example.com", "name": "User 1", "password_hash": "...", "role": "user"},
                {"email": "user2@example.com", "name": "User 2", "password_hash": "...", "role": "user"}
            ],
            "atomic": true
        }
    """
    if request.operation != BulkOperationType.CREATE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type for create endpoint"
        )
    
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items list cannot be empty"
        )
    
    if len(request.items) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 items per request"
        )
    
    result = bulk_handler.bulk_create(
        db,
        User,
        request.items,
        atomic=request.atomic
    )
    
    return result


@router.post("/users/update", response_model=BulkOperationResult)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_update_users(
    request: BulkOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk update multiple users.
    
    Admin-only operation. Each item must contain 'id' field.
    
    Args:
        request: Bulk operation request with list of user data to update
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        BulkOperationResult with status of each updated user
        
    Raises:
        HTTPException: If not authorized or operation type mismatch
        
    Example:
        {
            "operation": "update",
            "items": [
                {"id": 1, "name": "Updated User 1"},
                {"id": 2, "role": "admin"}
            ],
            "atomic": true
        }
    """
    if request.operation != BulkOperationType.UPDATE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type for update endpoint"
        )
    
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items list cannot be empty"
        )
    
    result = bulk_handler.bulk_update(
        db,
        User,
        request.items,
        key_field="id",
        atomic=request.atomic
    )
    
    return result


@router.post("/users/delete", response_model=BulkOperationResult)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_delete_users(
    ids: List[int],
    atomic: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk delete multiple users.
    
    Admin-only operation.
    
    Args:
        ids: List of user IDs to delete
        atomic: If true, all-or-nothing; if false, partial success allowed
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        BulkOperationResult with status of each deleted user
        
    Raises:
        HTTPException: If not authorized or no IDs provided
    """
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IDs list cannot be empty"
        )
    
    result = bulk_handler.bulk_delete(
        db,
        User,
        ids,
        key_field="id",
        atomic=atomic
    )
    
    return result


@router.post("/analyses/create", response_model=BulkOperationResult, status_code=201)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_create_analyses(
    request: BulkOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk create multiple analyses.
    
    Creates analyses for the current user. Admin can create for any user.
    
    Args:
        request: Bulk operation request with list of analysis data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BulkOperationResult with status of each created analysis
        
    Raises:
        HTTPException: If operation type mismatch or validation fails
        
    Example:
        {
            "operation": "create",
            "items": [
                {
                    "user_id": 1,
                    "resume_text": "...",
                    "jd_text": "...",
                    "extracted_resume_skills": [...],
                    "extracted_jd_skills": [...],
                    "missing_skills": [...],
                    "matched_skills": [...],
                    "learning_path": {...},
                    "reasoning_trace": {...}
                }
            ],
            "atomic": true
        }
    """
    if request.operation != BulkOperationType.CREATE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type for create endpoint"
        )
    
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items list cannot be empty"
        )
    
    # If not admin, set user_id to current user
    if current_user.role != UserRole.ADMIN:
        for item in request.items:
            item["user_id"] = current_user.id
    
    result = bulk_handler.bulk_create(
        db,
        Analysis,
        request.items,
        atomic=request.atomic
    )
    
    return result


@router.post("/analyses/update", response_model=BulkOperationResult)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_update_analyses(
    request: BulkOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk update multiple analyses.
    
    Users can only update their own analyses. Admin can update any.
    Each item must contain 'id' field.
    
    Args:
        request: Bulk operation request with list of analysis data to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BulkOperationResult with status of each updated analysis
        
    Raises:
        HTTPException: If not authorized or operation type mismatch
        
    Example:
        {
            "operation": "update",
            "items": [
                {"id": 1, "learning_path": {...}},
                {"id": 2, "reasoning_trace": {...}}
            ],
            "atomic": false
        }
    """
    if request.operation != BulkOperationType.UPDATE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type for update endpoint"
        )
    
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items list cannot be empty"
        )
    
    # Check authorization if not admin
    if current_user.role != UserRole.ADMIN:
        analysis_ids = [item.get("id") for item in request.items if "id" in item]
        unauthorized = db.query(Analysis).filter(
            Analysis.id.in_(analysis_ids),
            Analysis.user_id != current_user.id
        ).first()
        
        if unauthorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this analysis"
            )
    
    result = bulk_handler.bulk_update(
        db,
        Analysis,
        request.items,
        key_field="id",
        atomic=request.atomic
    )
    
    return result


@router.post("/analyses/delete", response_model=BulkOperationResult)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_delete_analyses(
    ids: List[int],
    atomic: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk delete multiple analyses.
    
    Users can only delete their own analyses. Admin can delete any.
    
    Args:
        ids: List of analysis IDs to delete
        atomic: If true, all-or-nothing; if false, partial success allowed
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BulkOperationResult with status of each deleted analysis
        
    Raises:
        HTTPException: If not authorized or no IDs provided
    """
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IDs list cannot be empty"
        )
    
    # Check authorization if not admin
    if current_user.role != UserRole.ADMIN:
        unauthorized = db.query(Analysis).filter(
            Analysis.id.in_(ids),
            Analysis.user_id != current_user.id
        ).first()
        
        if unauthorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this analysis"
            )
    
    result = bulk_handler.bulk_delete(
        db,
        Analysis,
        ids,
        key_field="id",
        atomic=atomic
    )
    
    return result


@router.post("/analyses/upsert", response_model=BulkOperationResult)
@limiter.limit(RateLimits.BULK_OPERATIONS)
async def bulk_upsert_analyses(
    request: BulkOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk upsert (create or update) multiple analyses.
    
    Items with 'id' will be updated; items without 'id' will be created.
    
    Args:
        request: Bulk operation request with analysis data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BulkOperationResult with status of each upserted analysis
        
    Raises:
        HTTPException: If operation type mismatch
        
    Example:
        {
            "operation": "upsert",
            "items": [
                {"id": 1, "learning_path": {...}},
                {"user_id": 1, "resume_text": "..."}
            ],
            "atomic": false
        }
    """
    if request.operation != BulkOperationType.UPSERT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type for upsert endpoint"
        )
    
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items list cannot be empty"
        )
    
    # If not admin, set user_id to current user for new items
    if current_user.role != UserRole.ADMIN:
        for item in request.items:
            if "id" not in item:  # New item
                item["user_id"] = current_user.id
    
    result = bulk_handler.bulk_upsert(
        db,
        Analysis,
        request.items,
        key_field="id",
        atomic=request.atomic
    )
    
    return result
