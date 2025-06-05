from typing import List, Dict, Any
import logging
from app.services.question_generator import QuestionGenerator
from app.services.chatgpt_question_generator import ChatGPTQuestionGenerator

logger = logging.getLogger(__name__)

async def generate_questions(
    content: str,
    num_questions: int = 5,
    difficulty: str = "mixed",
    use_openai: bool = False
) -> List[Dict[str, Any]]:
    """
    Generate questions using either the default or OpenAI-based generator.
    
    Args:
        content: The text content to generate questions from
        num_questions: Number of questions to generate
        difficulty: Question difficulty level (easy, medium, hard, mixed)
        use_openai: Whether to use OpenAI for generation
        
    Returns:
        List of generated questions
    """
    try:
        if use_openai:
            generator = ChatGPTQuestionGenerator()
        else:
            generator = QuestionGenerator()
            
        questions = await generator.generate_questions(
            content=content,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        return questions
        
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise 