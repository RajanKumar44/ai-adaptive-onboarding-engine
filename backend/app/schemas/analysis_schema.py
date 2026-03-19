"""
Analysis Pydantic schemas for validation and serialization.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any
from fastapi import UploadFile


class AnalysisBase(BaseModel):
    """Base analysis schema."""
    pass


class AnalysisCreate(BaseModel):
    """Schema for creating a new analysis."""
    user_id: int
    resume_text: str
    jd_text: str


class SkillAnalysisResult(BaseModel):
    """Result of skill extraction and comparison."""
    resume_skills: List[str]
    jd_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]


class RecommendationReasoning(BaseModel):
    """Reasoning for a single recommendation."""
    skill: str
    reason: str
    difficulty_level: str  # beginner, intermediate, advanced
    estimated_hours: int
    resources: List[str]


class LearningPathNode(BaseModel):
    """Single node in the learning path."""
    skill: str
    level: str
    steps: List[str]
    resources: List[Dict[str, str]]
    reasoning: str


class AnalysisResponse(BaseModel):
    """Complete analysis response."""
    id: int
    user_id: int
    resume_skills: List[str]
    jd_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    learning_path: List[LearningPathNode]
    reasoning: List[RecommendationReasoning]
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class AnalysisInDB(AnalysisResponse):
    """Analysis schema for database retrieval."""
    pass
