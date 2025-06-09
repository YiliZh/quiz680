from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class ExamSession(Base, TimestampMixin):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"))
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="exam_sessions")
    chapter = relationship("Chapter", back_populates="exam_sessions")
    attempts = relationship("QuestionAttempt", back_populates="exam_session", cascade="all, delete-orphan") 