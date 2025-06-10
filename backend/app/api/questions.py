from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models import Question, QuestionAttempt, ExamSession, Chapter, Upload
from app.schemas.question import QuestionCreateSchema, QuestionResponseSchema, AnswerSubmitSchema
from app.schemas.question_attempt import QuestionAttemptResponseSchema
from app.schemas.exam_session import ExamSessionWithDetails
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
    
    # Get or create an exam session for this chapter
    exam_session = db.query(ExamSession).filter(
        ExamSession.user_id == current_user.id,
        ExamSession.chapter_id == question.chapter_id,
        ExamSession.completed_at == None  # Only get active sessions
    ).first()
    
    if not exam_session:
        # Create a new exam session
        exam_session = ExamSession(
            user_id=current_user.id,
            chapter_id=question.chapter_id,
            score=0,
            total_questions=0,
            correct_answers=0,
            started_at=datetime.utcnow()
        )
        db.add(exam_session)
        db.commit()
        db.refresh(exam_session)
    
    # Create the attempt record
    attempt = QuestionAttempt(
        user_id=current_user.id,
        question_id=question_id,
        exam_session_id=exam_session.id,
        chosen_answer=answer.chosen_answer,
        is_correct=is_correct
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt 

@router.post("/complete-session/{chapter_id}", response_model=ExamSessionWithDetails)
async def complete_exam_session(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete an exam session and calculate the final score"""
    # Get the active exam session
    exam_session = db.query(ExamSession).filter(
        ExamSession.user_id == current_user.id,
        ExamSession.chapter_id == chapter_id,
        ExamSession.completed_at == None  # Only get active sessions
    ).first()
    
    if not exam_session:
        raise HTTPException(status_code=404, detail="No active exam session found")
    
    # Get all attempts for this session
    attempts = db.query(QuestionAttempt).filter(
        QuestionAttempt.exam_session_id == exam_session.id
    ).all()
    
    # Calculate score
    total_questions = len(attempts)
    correct_answers = sum(1 for attempt in attempts if attempt.is_correct)
    
    # Update exam session
    exam_session.total_questions = total_questions
    exam_session.correct_answers = correct_answers
    exam_session.score = correct_answers
    exam_session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(exam_session)
    
    # Get chapter and upload info for response
    chapter = db.query(Chapter).filter(Chapter.id == exam_session.chapter_id).first()
    upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
    
    # Prepare response
    session_dict = exam_session.__dict__
    session_dict["chapter_title"] = chapter.title
    session_dict["book_title"] = upload.filename
    
    # Add detailed logging for debugging
    logger.info(f"Processing exam session {exam_session.id}:")
    logger.info(f"Raw values - score: {exam_session.score} (type: {type(exam_session.score)}), total_questions: {exam_session.total_questions} (type: {type(exam_session.total_questions)})")
    
    # Safely calculate performance percentage
    try:
        total_questions = float(exam_session.total_questions or 0)
        score = float(exam_session.score or 0)
        logger.info(f"Converted values - score: {score}, total_questions: {total_questions}")
        
        if total_questions <= 0:
            logger.warning(f"Session {exam_session.id}: total_questions is {total_questions}, setting performance to 0.0")
            session_dict["performance_percentage"] = 0.0
        else:
            performance = (score / total_questions) * 100
            logger.info(f"Session {exam_session.id}: Calculated performance: {performance}%")
            session_dict["performance_percentage"] = performance
            
    except (TypeError, ValueError, ZeroDivisionError) as e:
        logger.error(f"Error calculating performance percentage for session {exam_session.id}: {str(e)}")
        logger.error(f"Problematic values - score: {exam_session.score}, total_questions: {exam_session.total_questions}")
        session_dict["performance_percentage"] = 0.0
  
    # Add attempt details
    attempts_list = []
    for attempt in attempts:
        question = db.query(Question).filter(Question.id == attempt.question_id).first()
        attempts_list.append({
            "question_text": question.question_text,
            "user_answer": attempt.chosen_answer,
            "correct_answer": question.correct_answer,
            "is_correct": attempt.is_correct,
            "explanation": question.explanation
        })
    session_dict["attempts"] = attempts_list
    
    return ExamSessionWithDetails(**session_dict) 