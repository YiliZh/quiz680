import logging
from typing import List, Dict, Any
from app.core.config import settings
import openai
from app.models.question import Question as QuestionModel
from app.models.chapter import Chapter as ChapterModel
from sqlalchemy.orm import Session
from app.services.llm import generate_questions as generate_with_existing_model

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = settings.OPENAI_API_KEY

async def generate_questions_with_openai(chapter_text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """Generate questions using OpenAI's API"""
    try:
        logger.info(f"Generating {num_questions} questions using OpenAI")
        
        prompt = f"""Generate {num_questions} multiple choice questions based on the following text. 
        Each question should have 4 options (A, B, C, D) and one correct answer.
        Format each question as a JSON object with the following structure:
        {{
            "question": "The question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "The correct option (A, B, C, or D)",
            "explanation": "Brief explanation of why this is the correct answer"
        }}

        Text to generate questions from:
        {chapter_text}

        Return only the JSON array of questions, nothing else."""

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates educational multiple choice questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        # Extract the questions from the response
        questions_text = response.choices[0].message.content
        logger.info("Successfully generated questions with OpenAI")
        
        # Parse the questions (you might need to add error handling here)
        import json
        questions = json.loads(questions_text)
        
        return questions

    except Exception as e:
        logger.error(f"Error generating questions with OpenAI: {str(e)}")
        raise

async def generate_questions(
    chapter_id: int,
    db: Session,
    use_openai: bool = False,
    num_questions: int = 5
) -> List[QuestionModel]:
    """Generate questions for a chapter using either the existing model or OpenAI"""
    try:
        # Get the chapter
        chapter = db.query(ChapterModel).filter(ChapterModel.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        logger.info(f"Generating questions for chapter {chapter_id} using {'OpenAI' if use_openai else 'existing model'}")

        # Generate questions using the selected method
        if use_openai:
            questions_data = await generate_questions_with_openai(chapter.content, num_questions)
        else:
            questions_data = await generate_with_existing_model(chapter.content, num_questions)

        # Create question records
        questions = []
        for q_data in questions_data:
            question = QuestionModel(
                chapter_id=chapter_id,
                question_text=q_data['question'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data.get('explanation', '')
            )
            db.add(question)
            questions.append(question)

        db.commit()
        logger.info(f"Successfully generated and saved {len(questions)} questions")
        return questions

    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        db.rollback()
        raise 