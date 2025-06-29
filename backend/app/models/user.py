from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships with string references to avoid circular imports
    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    question_attempts = relationship("QuestionAttempt", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    exam_sessions = relationship("ExamSession", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    review_recommendations = relationship("ReviewRecommendation", back_populates="user", cascade="all, delete-orphan", lazy="dynamic") 