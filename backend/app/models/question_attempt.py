from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime

class QuestionAttempt(Base, TimestampMixin):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id", ondelete="CASCADE"), nullable=True)
    chosen_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="question_attempts")
    question = relationship("Question", back_populates="attempts")
    exam_session = relationship("ExamSession", back_populates="attempts") 