"""
API routes for skill analysis endpoints.
Requires JWT authentication for all endpoints except health check.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_or_admin
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis_schema import AnalysisResponse, AnalysisCreate
from app.schemas.pagination import PaginationParams, PaginatedResponse, SortDirection
from app.core.filters import FilterOperator, QueryFilter, ValidFieldChecker, SortBuilder
from app.core.search import FullTextSearchEngine, SearchMode
from app.utils.file_handler import process_and_validate_file
from app.services.skill_extractor import SkillExtractor
from app.services.skill_gap import SkillGapAnalyzer
from app.services.learning_path import LearningPathGenerator
from app.services.resume_parser import ResumeParser
from app.middleware.rate_limiting import RateLimits, limiter
from typing import List, Optional
import json

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=dict, status_code=200)
@limiter.limit(RateLimits.ANALYZE)
async def analyze_resume_and_jd(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze resume and job description to identify skill gaps and generate learning path.
    
    **Authentication Required**: JWT Bearer token
    
    This endpoint:
    1. Extracts text from resume and JD files
    2. Extracts skills using rule-based approach
    3. Identifies skill gaps
    4. Generates personalized adaptive learning path
    5. Stores analysis in database
    6. Returns complete analysis with reasoning
    
    Args:
        resume_file: Uploaded resume (PDF or TXT)
        jd_file: Uploaded job description (PDF or TXT)
        current_user: Authenticated user (via JWT token)
        db: Database session
        
    Returns:
        Complete analysis with skills, gaps, and learning path
        
    Raises:
        HTTPException: If files invalid, user not authenticated, or processing fails
    """
    
    # Extract text from files
    resume_text = await process_and_validate_file(resume_file)
    jd_text = await process_and_validate_file(jd_file)
    
    if not resume_text or not jd_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from files"
        )
    
    # Extract skills from both documents
    resume_skills = SkillExtractor.rule_based_extraction(resume_text)
    jd_skills = SkillExtractor.rule_based_extraction(jd_text)
    
    # Normalize skills
    resume_skills = SkillExtractor.normalize_skills(resume_skills)
    jd_skills = SkillExtractor.normalize_skills(jd_skills)
    
    # Analyze skill gaps
    gap_report = SkillGapAnalyzer.generate_gap_report(
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        jd_text=jd_text
    )
    
    # Get all missing skills
    missing_skills = (
        gap_report["missing_skills"]["high_priority"] +
        gap_report["missing_skills"]["medium_priority"] +
        gap_report["missing_skills"]["low_priority"]
    )
    
    # Detect user experience level
    resume_info = ResumeParser.parse_resume(resume_text)
    user_experience_level = resume_info["experience_level"]
    
    # Generate adaptive learning path
    learning_path = LearningPathGenerator.generate_complete_roadmap(
        missing_skills=missing_skills,
        prioritized_skills=gap_report["missing_skills"],
        resume_text=resume_text,
        experience_level=user_experience_level
    )
    
    # Generate reasoning trace
    reasoning_trace = LearningPathGenerator.generate_reasoning_trace(
        missing_skills=missing_skills,
        jd_text=jd_text,
        matched_skills=gap_report["matched_skills"]
    )
    
    # Store analysis in database
    db_analysis = Analysis(
        user_id=current_user.id,
        resume_text=resume_text,
        jd_text=jd_text,
        extracted_resume_skills=resume_skills,
        extracted_jd_skills=jd_skills,
        missing_skills=missing_skills,
        matched_skills=gap_report["matched_skills"],
        learning_path=learning_path,
        reasoning_trace=reasoning_trace
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # Prepare response
    return {
        "analysis_id": db_analysis.id,
        "user_id": current_user.id,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": gap_report["matched_skills"],
        "missing_skills": missing_skills,
        "gap_analysis": {
            "match_percentage": gap_report["summary"]["match_percentage"],
            "total_jd_skills": gap_report["summary"]["total_jd_skills"],
            "matched_count": gap_report["summary"]["matched_skills_count"],
            "missing_count": gap_report["summary"]["missing_skills_count"],
        },
        "learning_path": learning_path,
        "reasoning": reasoning_trace,
        "estimated_learning_hours": LearningPathGenerator.estimate_total_learning_time(learning_path),
        "user_experience_level": user_experience_level,
    }


@router.get("/analysis/{analysis_id}", response_model=dict)
@limiter.limit(RateLimits.GENERAL)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a previously performed analysis.
    
    **Authentication Required**: JWT Bearer token
    
    Users can only access their own analyses, admins can access any.
    
    Args:
        analysis_id: ID of the analysis to retrieve
        current_user: Authenticated user (via JWT token)
        db: Database session
        
    Returns:
        Stored analysis data
        
    Raises:
        HTTPException: If analysis not found or unauthorized
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Check authorization: user can view own analyses, admin can view all
    if analysis.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this analysis"
        )
    
    return {
        "analysis_id": analysis.id,
        "user_id": analysis.user_id,
        "resume_skills": analysis.extracted_resume_skills,
        "jd_skills": analysis.extracted_jd_skills,
        "matched_skills": analysis.matched_skills,
        "missing_skills": analysis.missing_skills,
        "learning_path": analysis.learning_path,
        "reasoning": analysis.reasoning_trace,
        "created_at": analysis.created_at.isoformat(),
    }


@router.get("/users/{user_id}/analyses")
@limiter.limit(RateLimits.GENERAL)
async def get_user_analyses(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    sort_by: Optional[str] = Query(None, description="Field to sort by (created_at, id)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, description="Search in resume and JD text"),
    filter_by_skills: Optional[List[str]] = Query(None, description="Filter by missing skills"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all analyses for a user with pagination, sorting, filtering, and search.
    
    **Authentication Required**: JWT Bearer token
    
    Users can list their own analyses, admins can list any user's analyses.
    
    **Features**:
    - Pagination: skip/limit parameters
    - Sorting: sort_by (created_at, id) with asc/desc
    - Filtering: filter_by_skills to find analyses with specific missing skills
    - Search: Full-text search across resume and JD text
    
    Args:
        user_id: User ID to get analyses for
        skip: Number of items to skip (pagination)
        limit: Number of items to return (pagination, max 100)
        sort_by: Field to sort by (created_at, id)
        sort_order: Sort order (asc or desc)
        search: Search term for full-text search
        filter_by_skills: List of skills to filter by
        current_user: Authenticated user (via JWT token)
        db: Database session
        
    Returns:
        Paginated list of user's analyses with total count and metadata
        
    Raises:
        HTTPException: If user not found or unauthorized
        
    Example:
        GET /api/v1/users/1/analyses?skip=0&limit=10&sort_by=created_at&sort_order=desc&search=python&filter_by_skills=Python&filter_by_skills=Docker
    """
    # Check authorization
    if user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this user's analyses"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Start with base query
    query = db.query(Analysis).filter(Analysis.user_id == user_id)
    
    # Apply search
    if search:
        search_engine = FullTextSearchEngine(Analysis)
        search_engine.add_field(Analysis.resume_text, weight=1.5)
        search_engine.add_field(Analysis.jd_text, weight=1.5)
        
        # Build search expression for resume and JD
        search_expr = search_engine.builder.search(search, SearchMode.SIMPLE)
        if search_expr:
            query = query.filter(search_expr)
    
    # Get total before pagination
    total = query.count()
    
    # Apply sorting
    if sort_by:
        valid_fields = ValidFieldChecker(Analysis)
        if valid_fields.is_valid(sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(getattr(Analysis, sort_by).desc())
            else:
                query = query.order_by(getattr(Analysis, sort_by).asc())
        else:
            # Default to created_at desc
            query = query.order_by(Analysis.created_at.desc())
    else:
        # Default sorting
        query = query.order_by(Analysis.created_at.desc())
    
    # Apply pagination
    analyses = query.offset(skip).limit(limit).all()
    
    # Build response
    analyses_list = [
        {
            "analysis_id": a.id,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            "match_percentage": len(a.matched_skills) / len(a.extracted_jd_skills) * 100 if a.extracted_jd_skills else 0,
            "missing_skills_count": len(a.missing_skills),
            "matched_skills_count": len(a.matched_skills),
            "total_jd_skills": len(a.extracted_jd_skills),
            "missing_skills": a.missing_skills[:5] if a.missing_skills else [],  # First 5
        }
        for a in analyses
    ]
    
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "user_id": user_id,
        "data": analyses_list,
        "total": total,
        "skip": skip,
        "limit": limit,
        "page": page,
        "pages": pages,
        "has_next": (skip + limit) < total,
        "has_prev": skip > 0,
        "search_query": search,
        "sort_by": sort_by or "created_at",
        "sort_order": sort_order
    }


@router.get("/health")
@limiter.limit(RateLimits.HEALTH)
async def health_check():
    """
    Health check endpoint for monitoring.
    Public endpoint (no authentication required).
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "AI Adaptive Onboarding Engine API",
        "version": "1.0.0"
    }
