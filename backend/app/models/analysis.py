"""
Analysis model for storing skill analysis results.
"""

from sqlalchemy import Column, Integer, ForeignKey, JSON, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.base import AuditedBase


class Analysis(Base, AuditedBase):
    """
    Analysis model for storing resume and job description analysis results.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        resume_text: Extracted text from resume PDF
        jd_text: Extracted text from job description
        extracted_resume_skills: List of skills found in resume (JSON)
        extracted_jd_skills: List of skills found in job description (JSON)
        missing_skills: Skills required in JD but missing in resume (JSON)
        matched_skills: Skills found in both resume and JD (JSON)
        learning_path: Personalized adaptive learning roadmap (JSON)
        reasoning_trace: Reasoning for each recommendation (JSON)
        created_at: Analysis creation timestamp
        created_by: User ID who created this analysis
        updated_at: Last update timestamp
        updated_by: User ID who last updated this analysis
        deleted_at: When analysis was soft deleted
        user: Relationship to User
    """
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Input data
    resume_text = Column(Text, nullable=False)
    jd_text = Column(Text, nullable=False)
    
    # Extracted skills
    extracted_resume_skills = Column(JSON, nullable=False)  # List of skills from resume
    extracted_jd_skills = Column(JSON, nullable=False)  # List of skills from JD
    
    # Analysis results
    missing_skills = Column(JSON, nullable=False)  # Skills in JD but not in resume
    matched_skills = Column(JSON, nullable=False)  # Skills found in both
    
    # Learning recommendations
    learning_path = Column(JSON, nullable=False)  # Detailed learning roadmap
    reasoning_trace = Column(JSON, nullable=False)  # Reasoning for each recommendation
    
    # Relationship to User
    user = relationship("User", back_populates="analyses")
    feedback_entries = relationship("AnalysisFeedback", back_populates="analysis", cascade="all, delete-orphan")
    
    # Indexes for frequently queried fields
    __table_args__ = (
        Index('ix_analyses_user_id_not_deleted', 'user_id', 'deleted_at'),
        Index('ix_analyses_user_created', 'user_id', 'created_at'),
    )
