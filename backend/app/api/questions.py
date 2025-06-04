from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.deps import get_db, get_current_user
from app.models import Question, QuestionAttempt
from app.schemas import QuestionCreateSchema, QuestionResponseSchema, AnswerSubmitSchema, QuestionAttemptResponseSchema
from app.services.quiz import generate_questions
from app.services.question_generator import QuestionGenerator
from app.services.chatgpt_question_generator import ChatGPTQuestionGenerator
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{chapter_id}/questions", response_model=List[QuestionResponseSchema])
def get_questions(chapter_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")
    return questions

@router.post("/generate", response_model=List[QuestionResponseSchema])
async def generate_questions(
    content: str = Form(...),
    num_questions: int = Form(5),
    difficulty: str = Form("mixed"),
    generator_type: str = Form("default"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate questions based on content using either default or ChatGPT generator.
    """
    try:
        if generator_type == "chatgpt":
            generator = ChatGPTQuestionGenerator()
        else:
            generator = QuestionGenerator()

        questions = await generator.generate_questions(
            content=content,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        # Save questions to database
        db_questions = []
        for q in questions:
            db_question = Question(
                question_text=q["question_text"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                question_type=q["question_type"],
                difficulty=q.get("difficulty", "medium"),
                chapter_id=current_user.current_chapter_id
            )
            db.add(db_question)
            db_questions.append(db_question)
        
        db.commit()
        for q in db_questions:
            db.refresh(q)
        
        return db_questions
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{question_id}/answer", response_model=QuestionAttemptResponseSchema)
async def submit_answer(
    question_id: int,
    answer: AnswerSubmitSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit an answer to a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = False
    
    if question.question_type == "multiple_choice":
        # Get the index of the correct answer in the options array
        correct_index = ord(question.correct_answer) - ord('A')
        if correct_index < 0 or correct_index >= len(question.options):
            raise HTTPException(status_code=500, detail="Invalid correct answer format")
        
        # Get the correct answer text
        correct_answer_text = question.options[correct_index]
        
        # Check if the answer matches either the letter or the text
        is_correct = (
            answer.chosen_answer == question.correct_answer or  # Letter match (A, B, C, D)
            answer.chosen_answer == correct_answer_text  # Text match
        )
    elif question.question_type == "true_false":
        # For true/false questions, handle both letter and text formats
        correct_answer = question.correct_answer.lower()
        chosen_answer = answer.chosen_answer.lower()
        
        # Map letter answers to True/False
        if chosen_answer in ['a', 'b']:
            chosen_answer = 'true' if chosen_answer == 'a' else 'false'
        
        is_correct = chosen_answer == correct_answer
    
    # Create the attempt record
    attempt = QuestionAttempt(
        user_id=current_user.id,
        question_id=question_id,
        chosen_answer=answer.chosen_answer,
        is_correct=is_correct
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt 