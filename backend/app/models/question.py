from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    q_text = Column(Text, nullable=False)
    options = Column(ARRAY(String), nullable=False)
    correct_idx = Column(Integer, nullable=False)
    explanation = Column(Text)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)

    chapter = relationship("Chapter", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question", cascade="all, delete-orphan") 