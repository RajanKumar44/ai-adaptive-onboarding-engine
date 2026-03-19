from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


class LearningStep(BaseModel):
    step: int
    title: str
    description: str
    resources: List[str]
    estimated_hours: int


class SkillLearningPath(BaseModel):
    skill: str
    current_level: str
    target_level: str
    priority: str
    steps: List[LearningStep]
    total_hours: int


class AnalysisRequest(BaseModel):
    email: EmailStr
    resume_text: str
    jd_text: str


class AnalysisResponse(BaseModel):
    id: int
    email: str
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float
    learning_path: List[SkillLearningPath]
    reasoning_trace: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisDetailResponse(BaseModel):
    id: int
    user_id: int
    resume_text: str
    jd_text: str
    extracted_resume_skills: List[str]
    extracted_jd_skills: List[str]
    missing_skills: List[str]
    matched_skills: List[str]
    learning_path: List[Dict[str, Any]]
    reasoning_trace: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
