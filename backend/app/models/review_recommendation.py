from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class ReviewRecommendation(Base, TimestampMixin):
    __tablename__ = "review_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=False)
    review_stage = Column(Integer, default=1)  # 1: 1 day, 2: 7 days, 3: 16 days, 4: 35 days

    # Relationships
    user = relationship("User", back_populates="review_recommendations")
    question = relationship("Question", back_populates="review_recommendations") 