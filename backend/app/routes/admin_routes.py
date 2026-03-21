"""
API routes for user management and administration.
Requires JWT authentication with appropriate roles.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_admin
from app.models.user import User, UserRole
from app.models.analysis import Analysis
from app.models.feedback import AnalysisFeedback
from app.schemas.auth_schema import UserResponse, UserDetailResponse
from app.core.filters import ValidFieldChecker
from app.core.search import FullTextSearchEngine, SearchMode
from app.middleware.rate_limiting import RateLimits, limiter
from typing import List, Optional
from datetime import datetime
import math

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def _month_key(value: datetime) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def _month_label(value: datetime) -> str:
    return value.strftime("%b %Y")


def _program_name(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return "General"
    return " ".join(word.capitalize() for word in text.replace("_", " ").replace("-", " ").split())


def _recency_weight(timestamp: datetime, now: datetime) -> float:
    """Apply exponential decay so recent feedback contributes more."""
    age_days = max((now - timestamp).total_seconds() / 86400.0, 0.0)
    half_life_days = 45.0
    return math.exp(-math.log(2.0) * age_days / half_life_days)


@router.get("/feedback-analytics", response_model=dict)
@limiter.limit(RateLimits.GENERAL)
async def get_feedback_analytics(
    request: Request,
    months: int = Query(6, ge=1, le=24, description="Number of months to include in trend"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get feedback analytics for admins.

    Includes response counts, weighted satisfaction trend, and per-program averages.
    """
    now = datetime.utcnow()

    month_buckets = []
    month_map = {}
    for offset in range(months - 1, -1, -1):
        month_start = datetime(now.year, now.month, 1)
        year = month_start.year
        month = month_start.month - offset
        while month <= 0:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        bucket_date = datetime(year, month, 1)
        key = _month_key(bucket_date)
        bucket = {
            "month": _month_label(bucket_date),
            "responses": 0,
            "sum_rating": 0.0,
            "weighted_sum": 0.0,
            "weight_sum": 0.0,
        }
        month_buckets.append(bucket)
        month_map[key] = bucket

    rows = db.query(AnalysisFeedback, Analysis).join(
        Analysis,
        AnalysisFeedback.analysis_id == Analysis.id,
    ).all()

    total_responses = 0
    total_sum_rating = 0.0
    total_weighted_sum = 0.0
    total_weight_sum = 0.0
    program_stats = {}

    for feedback, analysis in rows:
        event_time = feedback.updated_at or feedback.created_at or analysis.created_at
        if not event_time:
            continue

        rating = float(feedback.rating)
        weight = _recency_weight(event_time, now)

        total_responses += 1
        total_sum_rating += rating
        total_weighted_sum += rating * weight
        total_weight_sum += weight

        key = _month_key(event_time)
        if key in month_map:
            bucket = month_map[key]
            bucket["responses"] += 1
            bucket["sum_rating"] += rating
            bucket["weighted_sum"] += rating * weight
            bucket["weight_sum"] += weight

        skill_list = analysis.missing_skills if isinstance(analysis.missing_skills, list) else []
        program_names = {_program_name(skill) for skill in skill_list if str(skill).strip()}
        if not program_names:
            program_names = {"General"}

        for name in program_names:
            if name not in program_stats:
                program_stats[name] = {
                    "responses": 0,
                    "sum_rating": 0.0,
                    "weighted_sum": 0.0,
                    "weight_sum": 0.0,
                }
            program_stats[name]["responses"] += 1
            program_stats[name]["sum_rating"] += rating
            program_stats[name]["weighted_sum"] += rating * weight
            program_stats[name]["weight_sum"] += weight

    trend = []
    for bucket in month_buckets:
        avg_rating = (bucket["sum_rating"] / bucket["responses"]) if bucket["responses"] else 0.0
        weighted_avg = (bucket["weighted_sum"] / bucket["weight_sum"]) if bucket["weight_sum"] else 0.0
        trend.append({
            "month": bucket["month"],
            "responses": bucket["responses"],
            "average_rating": round(avg_rating, 2),
            "weighted_average_rating": round(weighted_avg, 2),
            "weighted_satisfaction_percent": round((weighted_avg / 5.0) * 100.0, 1),
        })

    per_program_average = []
    for name, stats in program_stats.items():
        avg_rating = (stats["sum_rating"] / stats["responses"]) if stats["responses"] else 0.0
        weighted_avg = (stats["weighted_sum"] / stats["weight_sum"]) if stats["weight_sum"] else 0.0
        per_program_average.append({
            "program": name,
            "responses": stats["responses"],
            "average_rating": round(avg_rating, 2),
            "weighted_average_rating": round(weighted_avg, 2),
            "weighted_satisfaction_percent": round((weighted_avg / 5.0) * 100.0, 1),
        })

    per_program_average.sort(key=lambda item: (-item["responses"], -item["weighted_average_rating"]))

    average_rating = (total_sum_rating / total_responses) if total_responses else 0.0
    weighted_average_rating = (total_weighted_sum / total_weight_sum) if total_weight_sum else 0.0

    return {
        "summary": {
            "response_count": total_responses,
            "average_rating": round(average_rating, 2),
            "weighted_average_rating": round(weighted_average_rating, 2),
            "weighted_satisfaction_percent": round((weighted_average_rating / 5.0) * 100.0, 1),
            "half_life_days": 45,
        },
        "trend": trend,
        "per_program_average": per_program_average,
    }


@router.get("/users", response_model=dict)
@limiter.limit(RateLimits.GENERAL)
async def list_all_users(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    sort_by: Optional[str] = Query(None, description="Field to sort by (created_at, name, email, role)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, description="Search in name and email"),
    filter_role: Optional[str] = Query(None, description="Filter by role (admin, user, guest)"),
    filter_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all users in the system with pagination, sorting, filtering, and search.
    
    **Admin Access Required**
    
    **Features**:
    - Pagination: skip/limit parameters
    - Sorting: sort_by (created_at, name, email, role) with asc/desc
    - Filtering: filter_role and filter_active
    - Search: Full-text search in name and email
    
    Args:
        skip: Number of items to skip (pagination)
        limit: Number of items to return (pagination, max 100)
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        search: Search term for full-text search
        filter_role: Filter by role (admin, user, guest)
        filter_active: Filter by active status
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Paginated list of users with total count and metadata
        
    Example:
        GET /api/v1/admin/users?skip=0&limit=10&sort_by=created_at&sort_order=desc&search=john&filter_role=admin&filter_active=true
    """
    # Start with base query
    query = db.query(User)
    
    # Apply search
    if search:
        search_engine = FullTextSearchEngine(User)
        search_engine.add_field(User.name, weight=2.0)
        search_engine.add_field(User.email, weight=1.5)
        
        search_expr = search_engine.builder.search(search, SearchMode.SIMPLE)
        if search_expr:
            query = query.filter(search_expr)
    
    # Apply role filter
    if filter_role:
        try:
            role_enum = UserRole(filter_role.lower())
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {filter_role}"
            )
    
    # Apply active filter
    if filter_active is not None:
        query = query.filter(User.is_active == filter_active)
    
    # Get total before pagination
    total = query.count()
    
    # Apply sorting
    if sort_by:
        valid_fields = ValidFieldChecker(User)
        if valid_fields.is_valid(sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(getattr(User, sort_by).desc())
            else:
                query = query.order_by(getattr(User, sort_by).asc())
        else:
            # Default to created_at desc
            query = query.order_by(User.created_at.desc())
    else:
        # Default sorting
        query = query.order_by(User.created_at.desc())
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    # Build response
    users_list = [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "analyses_count": len(user.analyses)
        }
        for user in users
    ]
    
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "data": users_list,
        "total": total,
        "skip": skip,
        "limit": limit,
        "page": page,
        "pages": pages,
        "has_next": (skip + limit) < total,
        "has_prev": skip > 0,
        "search_query": search,
        "filter_role": filter_role,
        "filter_active": filter_active,
        "sort_by": sort_by or "created_at",
        "sort_order": sort_order
    }


@router.get("/users/{user_id}", response_model=UserDetailResponse)
@limiter.limit(RateLimits.GENERAL)
async def get_user_details(
    request: Request,
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user.
    
    **Admin Access Required**
    
    Args:
        user_id: ID of user to retrieve
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Detailed user information
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        analyses_count=len(user.analyses)
    )


@router.put("/users/{user_id}/role", response_model=UserResponse)
@limiter.limit(RateLimits.GENERAL)
async def update_user_role(
    request: Request,
    user_id: int,
    new_role: UserRole,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    
    **Admin Access Required**
    
    Args:
        user_id: ID of user to update
        new_role: New role for the user (admin, user, guest)
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent demoting the last admin
    if user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last admin user"
            )
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.put("/users/{user_id}/deactivate", response_model=UserResponse)
@limiter.limit(RateLimits.GENERAL)
async def deactivate_user(
    request: Request,
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account.
    
    **Admin Access Required**
    
    Args:
        user_id: ID of user to deactivate
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or is the last admin
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating the last admin
    if user.role == UserRole.ADMIN:
        admin_count = db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active admin"
            )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.put("/users/{user_id}/activate", response_model=UserResponse)
@limiter.limit(RateLimits.GENERAL)
async def activate_user(
    request: Request,
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Activate a deactivated user account.
    
    **Admin Access Required**
    
    Args:
        user_id: ID of user to activate
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.delete("/users/{user_id}", status_code=204)
@limiter.limit(RateLimits.GENERAL)
async def delete_user(
    request: Request,
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user account permanently.
    
    **Admin Access Required**
    
    Args:
        user_id: ID of user to delete
        current_admin: Current authenticated admin user
        db: Database session
        
    Raises:
        HTTPException: If user not found or is the last admin
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting the last admin
    if user.role == UserRole.ADMIN:
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user"
            )
    
    db.delete(user)
    db.commit()
