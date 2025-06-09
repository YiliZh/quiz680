from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer
    options = Column(ARRAY(Text), nullable=True)
    correct_answer = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"))
    explanation = Column(Text)

    # Relationships
    chapter = relationship("Chapter", back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question", cascade="all, delete-orphan")
    review_recommendations = relationship("ReviewRecommendation", back_populates="question", cascade="all, delete-orphan") 