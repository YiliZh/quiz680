from typing import List, Dict, Any
import logging
import random
import re
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from app.models import Chapter, Question
from app.schemas import QuestionCreateSchema

logger = logging.getLogger(__name__)

class QuestionGenerator:
    def __init__(self):
        logger.info("Initializing QuestionGenerator")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Initialize only the embedding model (more reliable)
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Successfully loaded SentenceTransformer model")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

    def generate_questions(self, chapter: Chapter, num_questions: int = 5) -> List[QuestionCreateSchema]:
        """
        Generate questions for a given chapter using rule-based and template approaches.
        """
        logger.info(f"Generating {num_questions} questions for chapter {chapter.id}")
        
        try:
            # Extract key information from the chapter
            sentences = self._extract_sentences(chapter.content)
            key_concepts = self._extract_key_concepts_simple(chapter.content)
            important_sentences = self._extract_important_sentences(chapter.content)
            
            if not sentences:
                logger.warning(f"No sentences extracted from chapter {chapter.id}")
                return []
            
            questions = []
            
            # Calculate distribution of question types
            mcq_count = max(1, num_questions // 2)
            tf_count = max(1, num_questions // 4)
            short_answer_count = max(1, num_questions - mcq_count - tf_count)
            
            logger.info(f"Question distribution: MCQ={mcq_count}, T/F={tf_count}, Short={short_answer_count}")
            
            # Generate different types of questions
            mcqs = self._generate_mcqs_simple(important_sentences, key_concepts, mcq_count, chapter)
            questions.extend(mcqs)
            
            tf_questions = self._generate_true_false_simple(important_sentences, tf_count, chapter)
            questions.extend(tf_questions)
            
            short_answers = self._generate_short_answer_simple(important_sentences, short_answer_count, chapter)
            questions.extend(short_answers)
            
            logger.info(f"Successfully generated {len(questions)} questions for chapter {chapter.id}")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions for chapter {chapter.id}: {str(e)}", exc_info=True)
            raise

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract and clean sentences from text."""
        if not text:
            return []
        
        # Split by periods, exclamation marks, and question marks
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Filter out very short sentences, page numbers, headers, etc.
            if (len(sentence) > 20 and 
                not sentence.isdigit() and 
                not re.match(r'^(page|chapter|section)\s*\d+', sentence.lower()) and
                len(sentence.split()) >= 4):
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences[:50]  # Limit to first 50 sentences

    def _extract_key_concepts_simple(self, text: str) -> List[str]:
        """Extract key concepts using simple word frequency analysis."""
        if not text:
            return []
        
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common stop words
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
            'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
            'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
            'such', 'take', 'than', 'them', 'well', 'were', 'what', 'your',
            'also', 'back', 'call', 'came', 'each', 'even', 'find', 'first',
            'give', 'hand', 'high', 'keep', 'last', 'left', 'life', 'live',
            'look', 'made', 'most', 'move', 'must', 'name', 'need', 'never',
            'only', 'open', 'part', 'place', 'right', 'said', 'same', 'seem',
            'show', 'small', 'tell', 'turn', 'used', 'want', 'ways', 'work',
            'world', 'year', 'years', 'young', 'chapter', 'page', 'section'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top concepts
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        key_concepts = [word for word, freq in sorted_words[:15] if freq > 1]
        
        logger.debug(f"Extracted key concepts: {key_concepts[:5]}")
        return key_concepts

    def _extract_important_sentences(self, text: str) -> List[str]:
        """Extract important sentences using keyword density and position."""
        sentences = self._extract_sentences(text)
        if not sentences:
            return []
        
        key_concepts = self._extract_key_concepts_simple(text)
        
        # Score sentences based on keyword density
        scored_sentences = []
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # Count key concepts in sentence
            for concept in key_concepts[:10]:  # Use top 10 concepts
                if concept in sentence_lower:
                    score += 1
            
            # Bonus for sentences at the beginning (often contain main ideas)
            if sentences.index(sentence) < len(sentences) * 0.3:
                score += 0.5
            
            # Bonus for longer sentences (often more informative)
            if len(sentence.split()) > 15:
                score += 0.3
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        important_sentences = [s[0] for s in scored_sentences[:15]]
        
        logger.debug(f"Extracted {len(important_sentences)} important sentences")
        return important_sentences

    def _generate_mcqs_simple(self, sentences: List[str], key_concepts: List[str], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate MCQs using template-based approach."""
        logger.info(f"Generating {count} MCQs using template approach")
        questions = []
        
        question_templates = [
            "What is the main concept discussed in the following context?",
            "According to the text, which statement is most accurate?",
            "What does the passage primarily focus on?",
            "Which of the following best describes the key idea?",
            "What is the central theme of this section?"
        ]
        
        for i in range(min(count, len(sentences))):
            try:
                sentence = sentences[i]
                
                # Extract key terms from the sentence
                sentence_words = re.findall(r'\b[a-zA-Z]{4,}\b', sentence.lower())
                relevant_concepts = [c for c in key_concepts if c in sentence.lower()]
                
                if not relevant_concepts:
                    continue
                
                # Create question
                question_text = random.choice(question_templates)
                
                # Create options
                correct_concept = relevant_concepts[0]
                options = [correct_concept.title()]
                
                # Add distractors
                other_concepts = [c for c in key_concepts if c != correct_concept]
                distractors = random.sample(other_concepts, min(3, len(other_concepts)))
                
                if len(distractors) < 3:
                    # Fill with generic distractors
                    generic_distractors = ["Data analysis", "Research methodology", "Statistical analysis", "Information processing", "System design"]
                    needed = 3 - len(distractors)
                    distractors.extend(random.sample(generic_distractors, min(needed, len(generic_distractors))))
                
                options.extend([d.title() for d in distractors[:3]])
                random.shuffle(options)
                
                # Find correct answer index
                correct_answer = chr(65 + options.index(correct_concept.title()))  # A, B, C, D
                
                question = QuestionCreateSchema(
                    question_text=f"{question_text}\n\nContext: {sentence[:200]}{'...' if len(sentence) > 200 else ''}",
                    question_type="multiple_choice",
                    options=options,
                    correct_answer=correct_answer,
                    difficulty="medium",
                    chapter_id=chapter.id
                )
                questions.append(question)
                logger.info(f"Generated MCQ {i+1}: {question_text}")
                
            except Exception as e:
                logger.error(f"Error generating MCQ {i+1}: {str(e)}")
                continue
        
        return questions

    def _generate_true_false_simple(self, sentences: List[str], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate True/False questions using template approach."""
        logger.info(f"Generating {count} True/False questions using template approach")
        questions = []
        
        tf_templates = [
            "The following statement is accurate based on the text:",
            "According to the passage, this statement is true:",
            "The text supports the following claim:",
            "Based on the content, this statement is correct:"
        ]
        
        for i in range(min(count, len(sentences))):
            try:
                sentence = sentences[i]
                
                # Create a true statement from the sentence
                template = random.choice(tf_templates)
                
                # Simplify the sentence for the statement
                simplified = sentence[:150] + ('...' if len(sentence) > 150 else '')
                
                # Randomly decide if this should be true or false
                is_true = random.choice([True, False])
                
                if is_true:
                    statement = simplified
                    correct_answer = "True"
                else:
                    # Create a false statement by modifying the original
                    statement = self._create_false_statement(simplified)
                    correct_answer = "False"
                
                question = QuestionCreateSchema(
                    question_text=f"{template}\n\n'{statement}'",
                    question_type="true_false",
                    options=["True", "False"],
                    correct_answer=correct_answer,
                    difficulty="medium",
                    chapter_id=chapter.id
                )
                questions.append(question)
                logger.info(f"Generated T/F question {i+1}")
                
            except Exception as e:
                logger.error(f"Error generating T/F question {i+1}: {str(e)}")
                continue
        
        return questions

    def _create_false_statement(self, statement: str) -> str:
        """Create a false statement by modifying the original."""
        # Simple modifications to make statements false
        modifications = [
            (r'\bnot\b', ''),  # Remove 'not'
            (r'\bis\b', 'is not'),  # Change 'is' to 'is not'
            (r'\bare\b', 'are not'),  # Change 'are' to 'are not'
            (r'\bcan\b', 'cannot'),  # Change 'can' to 'cannot'
            (r'\bwill\b', 'will not'),  # Change 'will' to 'will not'
        ]
        
        modified = statement
        for pattern, replacement in modifications:
            if re.search(pattern, statement, re.IGNORECASE):
                modified = re.sub(pattern, replacement, statement, count=1, flags=re.IGNORECASE)
                break
        
        # If no modification was made, add a negation
        if modified == statement:
            modified = f"It is not true that {statement.lower()}"
        
        return modified

    def _generate_short_answer_simple(self, sentences: List[str], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate short answer questions using template approach."""
        logger.info(f"Generating {count} Short Answer questions using template approach")
        questions = []
        
        sa_templates = [
            "What is the key concept mentioned in this context?",
            "What is the main topic being discussed?",
            "What is the primary focus of this section?",
            "What concept is being explained here?",
            "What is the central idea presented?"
        ]
        
        for i in range(min(count, len(sentences))):
            try:
                sentence = sentences[i]
                
                # Extract a key concept as the answer
                sentence_words = re.findall(r'\b[A-Z][a-z]+\b', sentence)  # Capitalized words
                if not sentence_words:
                    sentence_words = re.findall(r'\b[a-z]{4,}\b', sentence.lower())
                
                if not sentence_words:
                    continue
                
                # Choose the most relevant word as answer
                answer = sentence_words[0] if sentence_words else "concept"
                question_text = random.choice(sa_templates)
                
                question = QuestionCreateSchema(
                    question_text=f"{question_text}\n\nContext: {sentence[:200]}{'...' if len(sentence) > 200 else ''}",
                    question_type="short_answer",
                    options=[],
                    correct_answer=answer.title(),
                    difficulty="medium",
                    chapter_id=chapter.id
                )
                questions.append(question)
                logger.info(f"Generated Short Answer question {i+1}")
                
            except Exception as e:
                logger.error(f"Error generating Short Answer question {i+1}: {str(e)}")
                continue
        
        return questions