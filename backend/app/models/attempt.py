from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Attempt(Base, TimestampMixin):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chosen_idx = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    question = relationship("Question", back_populates="attempts")
    user = relationship("User", back_populates="attempts") 