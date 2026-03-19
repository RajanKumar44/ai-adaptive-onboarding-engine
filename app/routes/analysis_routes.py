from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis_schema import AnalysisDetailResponse, AnalysisRequest, AnalysisResponse
from app.services.learning_path import LearningPathGenerator
from app.services.resume_parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.skill_gap import SkillGapAnalyzer

router = APIRouter()

# Service singletons (stateless)
_resume_parser = ResumeParser()
_skill_extractor = SkillExtractor()
_skill_gap_analyzer = SkillGapAnalyzer()
_learning_path_generator = LearningPathGenerator()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_resume(request: AnalysisRequest, db: Session = Depends(get_db)):
    """Analyze a resume against a job description and persist the result."""
    # Upsert user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(email=request.email)
        db.add(user)
        db.flush()

    # Parse & extract skills
    resume_sections = _resume_parser.parse_text(request.resume_text)
    jd_sections = _resume_parser.parse_text(request.jd_text)

    resume_skills = _skill_extractor.extract_skills(resume_sections["full_text"])
    jd_skills = _skill_extractor.extract_skills(jd_sections["full_text"])

    # Analyse gaps
    gap_result = _skill_gap_analyzer.analyze(resume_skills, jd_skills)
    matched_skills: list = gap_result["matched_skills"]
    missing_skills: list = gap_result["missing_skills"]
    match_percentage: float = gap_result["match_percentage"]

    # Generate learning path
    learning_path = _learning_path_generator.generate_path(missing_skills, resume_skills)
    reasoning_trace = _learning_path_generator.generate_reasoning(
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        learning_path=learning_path,
        match_percentage=match_percentage,
    )

    # Persist analysis
    analysis = Analysis(
        user_id=user.id,
        resume_text=request.resume_text,
        jd_text=request.jd_text,
        extracted_resume_skills=resume_skills,
        extracted_jd_skills=jd_skills,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        learning_path=learning_path,
        reasoning_trace=reasoning_trace,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    db.refresh(user)

    return AnalysisResponse(
        id=analysis.id,
        email=user.email,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        match_percentage=match_percentage,
        learning_path=learning_path,
        reasoning_trace=reasoning_trace,
        created_at=analysis.created_at,
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific analysis by its ID."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.get("/analyses/user/{email}", response_model=list[AnalysisDetailResponse])
def get_user_analyses(email: str, db: Session = Depends(get_db)):
    """Retrieve all analyses for a given user email."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.analyses
