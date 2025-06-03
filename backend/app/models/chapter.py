from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Chapter(Base, TimestampMixin):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    chapter_no = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    keywords = Column(String(500))
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False)
    has_questions = Column(Boolean, nullable=False, default=False)

    upload = relationship("Upload", back_populates="chapters")
    questions = relationship("Question", back_populates="chapter", cascade="all, delete-orphan") 