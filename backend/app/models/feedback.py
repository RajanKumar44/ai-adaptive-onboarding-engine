"""
Feedback model for analysis outcome satisfaction.
"""

from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import AuditedBase


class AnalysisFeedback(Base, AuditedBase):
    """
    Stores user feedback (rating/comment) for an analysis result.

    One user can submit at most one feedback record per analysis.
    """

    __tablename__ = "analysis_feedback"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="feedback_entries")
    user = relationship("User", back_populates="feedback_entries")

    __table_args__ = (
        UniqueConstraint("analysis_id", "user_id", name="uq_feedback_analysis_user"),
        Index("ix_feedback_analysis_user", "analysis_id", "user_id"),
    )
