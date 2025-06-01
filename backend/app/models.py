from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    uploads = relationship("Upload", back_populates="user")

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    stored_path = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="uploads")
    chapters = relationship("Chapter", back_populates="upload")

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"))
    chapter_no = Column(Integer)
    title = Column(String)
    summary = Column(String)
    upload = relationship("Upload", back_populates="chapters")
    tags = relationship("ChapterTag", back_populates="chapter")
    questions = relationship("Question", back_populates="chapter")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)
    chapters = relationship("ChapterTag", back_populates="tag")

class ChapterTag(Base):
    __tablename__ = "chapter_tags"
    chapter_id = Column(Integer, ForeignKey("chapters.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    chapter = relationship("Chapter", back_populates="tags")
    tag = relationship("Tag", back_populates="chapters")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    q_text = Column(String)
    options = Column(JSON)
    answer_key = Column(Integer)
    explanation = Column(String)
    chapter = relationship("Chapter", back_populates="questions")
    attempts = relationship("QuizAttempt", back_populates="question")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    chosen_idx = Column(Integer)
    is_correct = Column(Boolean)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    question = relationship("Question", back_populates="attempts") 