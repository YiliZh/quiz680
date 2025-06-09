from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Upload(Base, TimestampMixin):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    file_path = Column(String(255))
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_logs = Column(Text)  # Store processing logs
    user_id = Column(Integer, ForeignKey("users.id"))
    has_questions = Column(Boolean, default=False)

    user = relationship("User", back_populates="uploads")
    chapters = relationship("Chapter", back_populates="upload", cascade="all, delete-orphan") 