from typing import List, Dict, Any
import logging
from transformers import T5ForConditionalGeneration, T5Tokenizer
from sentence_transformers import SentenceTransformer
import torch
import re
from app.models import Chapter, Question
from app.schemas import QuestionCreate

logger = logging.getLogger(__name__)

class QuestionGenerator:
    def __init__(self):
        logger.info("Initializing QuestionGenerator")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        try:
            self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-base').to(self.device)
            self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-base')
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Successfully loaded T5 and SentenceTransformer models")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

    def generate_questions(self, chapter: Chapter, num_questions: int = 5) -> List[QuestionCreate]:
        """
        Generate questions for a given chapter using multiple strategies.
        """
        logger.info(f"Generating {num_questions} questions for chapter {chapter.id}")
        
        try:
            # Extract key concepts and sentences
            key_concepts = self._extract_key_concepts(chapter.content)
            important_sentences = self._extract_important_sentences(chapter.content)
            
            questions = []
            
            # Generate different types of questions
            mcq_count = num_questions // 2
            tf_count = num_questions // 4
            short_answer_count = num_questions - mcq_count - tf_count
            
            # Generate Multiple Choice Questions
            mcqs = self._generate_mcqs(important_sentences, key_concepts, mcq_count)
            questions.extend(mcqs)
            
            # Generate True/False Questions
            tf_questions = self._generate_true_false(important_sentences, tf_count)
            questions.extend(tf_questions)
            
            # Generate Short Answer Questions
            short_answers = self._generate_short_answer(important_sentences, short_answer_count)
            questions.extend(short_answers)
            
            logger.info(f"Successfully generated {len(questions)} questions for chapter {chapter.id}")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions for chapter {chapter.id}: {str(e)}", exc_info=True)
            raise

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from the text using sentence embeddings."""
        logger.debug("Extracting key concepts from text")
        sentences = text.split('.')
        embeddings = self.embedding_model.encode(sentences)
        # Use clustering or other methods to identify key concepts
        # This is a simplified version
        return [s.strip() for s in sentences if len(s.strip()) > 20][:5]

    def _extract_important_sentences(self, text: str) -> List[str]:
        """Extract important sentences for question generation."""
        logger.debug("Extracting important sentences")
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        # Use sentence embeddings to find important sentences
        embeddings = self.embedding_model.encode(sentences)
        # This is a simplified version - in production, use more sophisticated methods
        return sentences[:10]

    def _generate_mcqs(self, sentences: List[str], key_concepts: List[str], count: int) -> List[QuestionCreate]:
        """Generate multiple choice questions."""
        logger.debug(f"Generating {count} MCQs")
        questions = []
        
        for sentence in sentences[:count]:
            try:
                # Prepare prompt for T5
                prompt = f"Generate a multiple choice question from: {sentence}"
                inputs = self.t5_tokenizer(prompt, return_tensors="pt").to(self.device)
                
                # Generate question
                outputs = self.t5_model.generate(
                    inputs["input_ids"],
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7
                )
                
                question_text = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Create question object
                question = QuestionCreate(
                    question_text=question_text,
                    question_type="multiple_choice",
                    options=["A", "B", "C", "D"],  # This should be generated
                    correct_answer="A",  # This should be determined
                    difficulty="medium"
                )
                questions.append(question)
                
            except Exception as e:
                logger.error(f"Error generating MCQ: {str(e)}")
                continue
                
        return questions

    def _generate_true_false(self, sentences: List[str], count: int) -> List[QuestionCreate]:
        """Generate true/false questions."""
        logger.debug(f"Generating {count} True/False questions")
        questions = []
        
        for sentence in sentences[:count]:
            try:
                # Prepare prompt for T5
                prompt = f"Generate a true/false question from: {sentence}"
                inputs = self.t5_tokenizer(prompt, return_tensors="pt").to(self.device)
                
                # Generate question
                outputs = self.t5_model.generate(
                    inputs["input_ids"],
                    max_length=100,
                    num_return_sequences=1,
                    temperature=0.7
                )
                
                question_text = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Create question object
                question = QuestionCreate(
                    question_text=question_text,
                    question_type="true_false",
                    options=["True", "False"],
                    correct_answer="True",  # This should be determined
                    difficulty="medium"
                )
                questions.append(question)
                
            except Exception as e:
                logger.error(f"Error generating True/False question: {str(e)}")
                continue
                
        return questions

    def _generate_short_answer(self, sentences: List[str], count: int) -> List[QuestionCreate]:
        """Generate short answer questions."""
        logger.debug(f"Generating {count} Short Answer questions")
        questions = []
        
        for sentence in sentences[:count]:
            try:
                # Prepare prompt for T5
                prompt = f"Generate a short answer question from: {sentence}"
                inputs = self.t5_tokenizer(prompt, return_tensors="pt").to(self.device)
                
                # Generate question
                outputs = self.t5_model.generate(
                    inputs["input_ids"],
                    max_length=100,
                    num_return_sequences=1,
                    temperature=0.7
                )
                
                question_text = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Create question object
                question = QuestionCreate(
                    question_text=question_text,
                    question_type="short_answer",
                    options=[],  # No options for short answer
                    correct_answer="",  # This should be determined
                    difficulty="medium"
                )
                questions.append(question)
                
            except Exception as e:
                logger.error(f"Error generating Short Answer question: {str(e)}")
                continue
                
        return questions 