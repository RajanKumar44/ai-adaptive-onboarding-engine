"""
Analysis model for storing skill analysis results.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Analysis(Base):
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
        updated_at: Last update timestamp
        user: Relationship to User
    """
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
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
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to User
    user = relationship("User", back_populates="analyses")
