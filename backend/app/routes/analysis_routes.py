"""
API routes for skill analysis endpoints.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.analysis_schema import AnalysisResponse, AnalysisCreate
from app.utils.file_handler import process_and_validate_file
from app.services.skill_extractor import SkillExtractor
from app.services.skill_gap import SkillGapAnalyzer
from app.services.learning_path import LearningPathGenerator
from app.services.resume_parser import ResumeParser
from typing import List, Optional
import json

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user account.
    
    Args:
        user: User creation data
        db: Database session
        
    Returns:
        Created user information
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/analyze", response_model=dict, status_code=200)
async def analyze_resume_and_jd(
    user_id: int = Form(...),
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze resume and job description to identify skill gaps and generate learning path.
    
    This endpoint:
    1. Extracts text from resume and JD files
    2. Extracts skills using rule-based approach
    3. Identifies skill gaps
    4. Generates personalized adaptive learning path
    5. Stores analysis in database
    6. Returns complete analysis with reasoning
    
    Args:
        user_id: User ID performing analysis
        resume_file: Uploaded resume (PDF or TXT)
        jd_file: Uploaded job description (PDF or TXT)
        db: Database session
        
    Returns:
        Complete analysis with skills, gaps, and learning path
    """
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Extract text from files
    resume_text = await process_and_validate_file(resume_file)
    jd_text = await process_and_validate_file(jd_file)
    
    if not resume_text or not jd_text:
        raise HTTPException(status_code=400, detail="Failed to extract text from files")
    
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
        user_id=user_id,
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
        "user_id": user_id,
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
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a previously performed analysis.
    
    Args:
        analysis_id: ID of the analysis to retrieve
        db: Database session
        
    Returns:
        Stored analysis data
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
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
async def get_user_analyses(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all analyses for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of user's analyses
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).all()
    
    return {
        "user_id": user_id,
        "analyses_count": len(analyses),
        "analyses": [
            {
                "analysis_id": a.id,
                "created_at": a.created_at.isoformat(),
                "match_percentage": len(a.matched_skills) / len(a.extracted_jd_skills) * 100 if a.extracted_jd_skills else 0,
                "missing_skills_count": len(a.missing_skills),
            }
            for a in analyses
        ]
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "AI Adaptive Onboarding Engine API",
        "version": "1.0.0"
    }
