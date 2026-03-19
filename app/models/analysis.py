from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_text = Column(Text, nullable=False)
    jd_text = Column(Text, nullable=False)
    extracted_resume_skills = Column(JSON, default=list)
    extracted_jd_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    matched_skills = Column(JSON, default=list)
    learning_path = Column(JSON, default=list)
    reasoning_trace = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analyses")
