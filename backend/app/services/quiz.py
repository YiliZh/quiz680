from typing import List
from sqlalchemy.orm import Session
from app.models import Question, Chapter

async def generate_questions(chapter_id: int, db: Session):
    """Generate questions for a chapter"""
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        # TODO: Implement proper question generation using LLM
        # For now, create a simple placeholder question
        question = Question(
            text="What is the main topic of this chapter?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            answer_key=0,
            chapter_id=chapter_id
        )
        db.add(question)
        db.commit()
        
    except Exception as e:
        # Log error but don't fail the entire process
        print(f"Error generating questions for chapter {chapter_id}: {str(e)}")
        raise e 