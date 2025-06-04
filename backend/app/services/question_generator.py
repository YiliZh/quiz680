from typing import List, Dict, Any, Tuple
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
        
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Successfully loaded SentenceTransformer model")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

    def generate_questions(self, chapter: Chapter, num_questions: int = 5) -> List[QuestionCreateSchema]:
        """
        Generate educational questions that help students understand the content.
        """
        logger.info(f"Generating {num_questions} questions for chapter {chapter.id}")
        
        try:
            # Extract and analyze content
            logger.info(f"Analyzing content for chapter {chapter.id}")
            content_analysis = self._analyze_content(chapter.content)
            if not content_analysis:
                logger.warning(f"Could not analyze content for chapter {chapter.id}")
                return []
            
            questions = []
            
            # Generate different types of questions with specific counts
            num_concept = num_questions // 3  # 1-2 concept questions
            num_application = num_questions // 3  # 1-2 application questions
            num_relationship = num_questions // 3  # 1-2 relationship questions
            num_remaining = num_questions - (num_concept + num_application + num_relationship)
            
            # Generate concept questions
            logger.info("Generating concept questions...")
            concept_questions = self._generate_concept_questions(content_analysis, num_concept, chapter)
            logger.info(f"Generated {len(concept_questions)} concept questions")
            questions.extend(concept_questions)
            
            # Generate application questions
            logger.info("Generating application questions...")
            application_questions = self._generate_application_questions(content_analysis, num_application, chapter)
            logger.info(f"Generated {len(application_questions)} application questions")
            questions.extend(application_questions)
            
            # Generate relationship questions
            logger.info("Generating relationship questions...")
            relationship_questions = self._generate_relationship_questions(content_analysis, num_relationship, chapter)
            logger.info(f"Generated {len(relationship_questions)} relationship questions")
            questions.extend(relationship_questions)
            
            # If we still don't have enough questions, generate from important sentences
            if len(questions) < num_questions:
                logger.info("Generating questions from important sentences...")
                sentence_questions = self._generate_sentence_questions(
                    content_analysis['important_sentences'],
                    num_questions - len(questions),
                    chapter
                )
                logger.info(f"Generated {len(sentence_questions)} questions from sentences")
                questions.extend(sentence_questions)
            
            # Shuffle the questions to mix different types
            random.shuffle(questions)
            
            logger.info(f"Successfully generated {len(questions)} questions for chapter {chapter.id}")
            
            # Log the generated questions for debugging
            for i, q in enumerate(questions, 1):
                logger.info(f"Question {i}:")
                logger.info(f"  Text: {q.question_text}")
                logger.info(f"  Type: {q.question_type}")
                logger.info(f"  Options: {q.options}")
                logger.info(f"  Correct Answer: {q.correct_answer}")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions for chapter {chapter.id}: {str(e)}", exc_info=True)
            raise

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract and clean sentences from text."""
        if not text:
            return []
        
        # Split by periods, exclamation marks, and question marks
        # Also handle common abbreviations to avoid false splits
        abbreviations = ['e.g.', 'i.e.', 'etc.', 'vs.', 'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Ph.D.']
        for abbr in abbreviations:
            text = text.replace(abbr, abbr.replace('.', '@'))
        
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            # Restore abbreviations
            for abbr in abbreviations:
                sentence = sentence.replace(abbr.replace('.', '@'), abbr)
            
            sentence = sentence.strip()
            
            # Filter out very short sentences, page numbers, headers, etc.
            if (len(sentence) > 20 and 
                not sentence.isdigit() and 
                not re.match(r'^(page|chapter|section)\s*\d+', sentence.lower()) and
                len(sentence.split()) >= 4 and
                not re.match(r'^\d+\.\s*$', sentence) and  # Filter out numbered list markers
                not re.match(r'^[A-Z]\.\s*$', sentence)):  # Filter out lettered list markers
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences[:50]  # Limit to first 50 sentences

    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze the content to identify key concepts, relationships, and learning points."""
        if not content:
            logger.warning("Empty content provided for analysis")
            return {}
        
        # Split into sections
        sections = self._split_into_sections(content)
        logger.info(f"Split content into {len(sections)} sections")
        
        analysis = {
            'sections': [],
            'key_concepts': set(),
            'relationships': [],
            'examples': [],
            'definitions': [],
            'procedures': [],
            'important_sentences': []  # Add this to store important sentences
        }
        
        for i, section in enumerate(sections, 1):
            logger.info(f"Analyzing section {i}/{len(sections)}")
            section_analysis = self._analyze_section(section)
            analysis['sections'].append(section_analysis)
            
            # Aggregate key concepts
            analysis['key_concepts'].update(section_analysis['key_concepts'])
            
            # Collect relationships, examples, definitions, and procedures
            analysis['relationships'].extend(section_analysis['relationships'])
            analysis['examples'].extend(section_analysis['examples'])
            analysis['definitions'].extend(section_analysis['definitions'])
            analysis['procedures'].extend(section_analysis['procedures'])
            
            # Add important sentences from this section
            analysis['important_sentences'].extend(section_analysis['important_sentences'])
        
        # Log analysis results
        logger.info(f"Analysis complete. Found:")
        logger.info(f"- {len(analysis['key_concepts'])} key concepts")
        logger.info(f"- {len(analysis['relationships'])} relationships")
        logger.info(f"- {len(analysis['examples'])} examples")
        logger.info(f"- {len(analysis['definitions'])} definitions")
        logger.info(f"- {len(analysis['procedures'])} procedures")
        logger.info(f"- {len(analysis['important_sentences'])} important sentences")
        
        return analysis

    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into meaningful sections."""
        # Split by headers, paragraphs, or other natural breaks
        sections = re.split(r'\n\s*\n|\n(?=\d+\.|\w+\.)', content)
        return [s.strip() for s in sections if s.strip()]

    def _analyze_section(self, section: str) -> Dict[str, Any]:
        """Analyze a section to identify its key components."""
        sentences = self._extract_sentences(section)
        logger.info(f"Extracted {len(sentences)} sentences from section")
        
        analysis = {
            'key_concepts': set(),
            'relationships': [],
            'examples': [],
            'definitions': [],
            'procedures': [],
            'important_sentences': []  # Add this to store important sentences
        }
        
        for sentence in sentences:
            # Identify definitions
            if re.search(r'\b(is|are|refers to|means|defined as|consists of|comprises|contains)\b', sentence, re.IGNORECASE):
                analysis['definitions'].append(sentence)
                analysis['important_sentences'].append(sentence)
            
            # Identify examples
            if re.search(r'\b(for example|such as|like|including|e\.g\.|i\.e\.|specifically|notably)\b', sentence, re.IGNORECASE):
                analysis['examples'].append(sentence)
                analysis['important_sentences'].append(sentence)
            
            # Identify procedures
            if re.search(r'\b(first|then|next|finally|step|process|procedure|method|approach|technique)\b', sentence, re.IGNORECASE):
                analysis['procedures'].append(sentence)
                analysis['important_sentences'].append(sentence)
            
            # Extract key concepts
            concepts = self._extract_key_concepts(sentence)
            analysis['key_concepts'].update(concepts)
            
            # Identify relationships
            relationships = self._extract_relationships(sentence)
            if relationships:
                analysis['relationships'].extend(relationships)
                analysis['important_sentences'].append(sentence)
            
            # Add sentences that contain key technical terms
            if any(concept in sentence for concept in concepts):
                analysis['important_sentences'].append(sentence)
        
        return analysis

    def _extract_key_concepts(self, sentence: str) -> List[str]:
        """Extract key concepts from a sentence."""
        concepts = []
        
        # Technical terms (words that appear in technical contexts)
        tech_terms = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', sentence)
        concepts.extend(tech_terms)
        
        # Important phrases (after key indicators)
        indicators = [
            'called', 'known as', 'referred to as', 'defined as',
            'consists of', 'comprises', 'contains', 'includes',
            'is a', 'are a', 'is an', 'are an',
            'refers to', 'means', 'represents'
        ]
        
        for indicator in indicators:
            if indicator in sentence.lower():
                # Extract the phrase after the indicator
                parts = sentence.lower().split(indicator)
                if len(parts) > 1:
                    phrase = parts[1].split('.')[0].strip()
                    if len(phrase.split()) <= 5:  # Limit phrase length
                        concepts.append(phrase)
        
        # Add any technical terms found in the sentence
        technical_terms = [
            'function', 'method', 'class', 'object', 'variable',
            'parameter', 'argument', 'return', 'type', 'interface',
            'module', 'package', 'library', 'framework', 'algorithm',
            'data structure', 'database', 'query', 'index', 'key',
            'value', 'array', 'list', 'dictionary', 'map', 'set',
            'tree', 'graph', 'node', 'edge', 'vertex', 'path'
        ]
        
        for term in technical_terms:
            if term in sentence.lower():
                concepts.append(term)
        
        return list(set(concepts))  # Remove duplicates

    def _extract_relationships(self, sentence: str) -> List[Tuple[str, str, str]]:
        """Extract relationships between concepts."""
        relationships = []
        
        # Look for relationship indicators
        indicators = {
            'is_a': ['is a', 'are a', 'is an', 'are an'],
            'has_a': ['has a', 'have a', 'contains', 'includes'],
            'can': ['can', 'could', 'may', 'might'],
            'requires': ['requires', 'needs', 'must have'],
            'leads_to': ['leads to', 'results in', 'causes', 'creates']
        }
        
        for rel_type, rel_indicators in indicators.items():
            for indicator in rel_indicators:
                if indicator in sentence.lower():
                    # Extract the concepts before and after the indicator
                    parts = sentence.lower().split(indicator)
                    if len(parts) > 1:
                        concept1 = parts[0].split()[-1]  # Last word before indicator
                        concept2 = parts[1].split('.')[0].strip().split()[0]  # First word after indicator
                        relationships.append((concept1, rel_type, concept2))
        
        return relationships

    def _generate_relationship_questions(self, analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate questions that test understanding of relationships between concepts."""
        questions = []
        
        # Generate questions from relationships
        for relationship in analysis['relationships']:
            if len(questions) >= count:
                break
            
            concept1, rel_type, concept2 = relationship
            
            # Create different types of relationship questions
            question_patterns = [
                f"What is the relationship between {concept1} and {concept2}?",
                f"How does {concept1} affect {concept2}?",
                f"Which statement best describes the relationship between {concept1} and {concept2}?",
                f"What happens to {concept2} when {concept1} changes?",
                f"Which of the following best explains how {concept1} and {concept2} are related?"
            ]
            
            question_text = random.choice(question_patterns)
            
            # Create options based on the relationship and related concepts
            correct_option = f"{concept1} {rel_type} {concept2}"
            other_options = self._generate_relationship_options(concept1, concept2, rel_type, analysis)
            
            if not other_options:
                continue
            
            options = [correct_option] + other_options[:3]
            random.shuffle(options)
            
            # Store the correct answer as a letter (A, B, C, D)
            correct_answer = chr(65 + options.index(correct_option))
            
            question = QuestionCreateSchema(
                question_text=question_text,
                question_type="multiple_choice",
                options=options,
                correct_answer=correct_answer,
                difficulty="medium",
                chapter_id=chapter.id
            )
            questions.append(question)
        
        return questions

    def _generate_relationship_options(self, concept1: str, concept2: str, rel_type: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate plausible but incorrect relationship options."""
        options = []
        
        # Get other relationships from the analysis
        other_relationships = [(c1, r, c2) for c1, r, c2 in analysis['relationships'] 
                              if (c1, r, c2) != (concept1, rel_type, concept2)]
        
        # Create options by combining concepts with different relationship types
        relationship_types = {
            'is_a': ['is a type of', 'is a kind of', 'is a form of'],
            'has_a': ['has a', 'contains', 'includes'],
            'can': ['can', 'is able to', 'has the ability to'],
            'requires': ['requires', 'needs', 'depends on'],
            'leads_to': ['leads to', 'results in', 'causes']
        }
        
        # Add options from other relationships
        for c1, r, c2 in other_relationships:
            option = f"{c1} {r} {c2}"
            options.append(option)
        
        # Add variations of the original relationship
        for rel_type, variations in relationship_types.items():
            for variation in variations:
                if variation != rel_type:
                    option = f"{concept1} {variation} {concept2}"
                    options.append(option)
        
        return options

    def _generate_concept_questions(self, analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate questions that test understanding of key concepts."""
        questions = []
        
        # Generate questions from definitions
        for definition in analysis['definitions']:
            if len(questions) >= count:
                break
                
            # Extract the concept being defined
            concept = self._extract_defined_concept(definition)
            if not concept:
                logger.debug(f"Could not extract concept from definition: {definition}")
                continue
            
            logger.info(f"Generating question for concept: {concept}")
            
            # Create different types of concept questions
            question_patterns = [
                f"What is the definition of {concept}?",
                f"Which of the following best describes {concept}?",
                f"What does {concept} refer to?",
                f"Which statement correctly defines {concept}?",
                f"What is the meaning of {concept} in this context?"
            ]
            
            question_text = random.choice(question_patterns)
            
            # Create options based on the definition and related concepts
            correct_option = re.sub(r'^\d+\s+', '', definition)  # Remove any prepended numbers
            other_options = self._generate_definition_options(concept, analysis)
            
            if not other_options:
                logger.warning(f"Could not generate enough options for concept: {concept}")
                continue
            
            options = [correct_option] + other_options[:3]
            random.shuffle(options)
            
            # Store the correct answer as a letter (A, B, C, D)
            correct_answer = chr(65 + options.index(correct_option))
            
            question = QuestionCreateSchema(
                question_text=question_text,
                question_type="multiple_choice",
                options=options,
                correct_answer=correct_answer,
                difficulty="medium",
                chapter_id=chapter.id
            )
            questions.append(question)
            logger.info(f"Generated question for concept {concept}")
        
        return questions

    def _generate_application_questions(self, analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate questions that test application of concepts."""
        questions = []
        
        # Generate questions from examples and procedures
        for example in analysis['examples']:
            if len(questions) >= count:
                break
            
            # Create a question about applying the concept
            concept = self._extract_concept_from_example(example)
            if not concept:
                logger.debug(f"Could not extract concept from example: {example}")
                continue
            
            logger.info(f"Generating application question for concept: {concept}")
            
            # Create different types of application questions
            question_patterns = [
                f"Which of the following is an example of {concept}?",
                f"Which scenario best demonstrates {concept}?",
                f"In which situation would {concept} be most applicable?",
                f"Which of the following represents a correct application of {concept}?",
                f"Which case study best illustrates the use of {concept}?"
            ]
            
            question_text = random.choice(question_patterns)
            
            # Create options based on the example and related concepts
            correct_option = re.sub(r'^\d+\s+', '', example)  # Remove any prepended numbers
            other_options = self._generate_example_options(concept, analysis)
            
            if not other_options:
                logger.warning(f"Could not generate enough options for concept: {concept}")
                continue
            
            options = [correct_option] + other_options[:3]
            random.shuffle(options)
            
            # Store the correct answer as a letter (A, B, C, D)
            correct_answer = chr(65 + options.index(correct_option))
            
            question = QuestionCreateSchema(
                question_text=question_text,
                question_type="multiple_choice",
                options=options,
                correct_answer=correct_answer,
                difficulty="medium",
                chapter_id=chapter.id
            )
            questions.append(question)
            logger.info(f"Generated application question for concept {concept}")
        
        return questions

    def _extract_defined_concept(self, definition: str) -> str:
        """Extract the concept being defined from a definition sentence."""
        # Look for patterns like "X is defined as..." or "X refers to..."
        patterns = [
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|are)\s+(?:defined as|refers to)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|are)\s+(?:a|an)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:means|refers to)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, definition)
            if match:
                return match.group(1)
        
        return ""

    def _generate_definition_options(self, concept: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate plausible but incorrect definition options."""
        options = []
        
        # Get other definitions from the analysis
        other_definitions = [d for d in analysis['definitions'] if concept not in d]
        
        # Get related concepts
        related_concepts = [c for c in analysis['key_concepts'] if c != concept]
        
        # Create options by combining related concepts with definition patterns
        definition_patterns = [
            f"{concept} is a type of {related_concept}",
            f"{concept} refers to the process of {related_concept}",
            f"{concept} is used to {related_concept}",
            f"{concept} is part of {related_concept}",
            f"{concept} is related to {related_concept}"
        ]
        
        for pattern in definition_patterns:
            for related_concept in related_concepts:
                option = pattern.format(concept=concept, related_concept=related_concept)
                # Remove any prepended numbers
                option = re.sub(r'^\d+\s+', '', option)
                options.append(option)
        
        return options

    def _extract_concept_from_example(self, example: str) -> str:
        """Extract the concept being exemplified from an example sentence."""
        # Look for patterns like "For example, X..." or "X such as..."
        patterns = [
            r'For example,\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+such as',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+including'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, example)
            if match:
                return match.group(1)
        
        return ""

    def _generate_example_options(self, concept: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate plausible but incorrect example options."""
        options = []
        
        # Get other examples from the analysis
        other_examples = [e for e in analysis['examples'] if concept not in e]
        
        # Get related concepts
        related_concepts = [c for c in analysis['key_concepts'] if c != concept]
        
        # Create options by combining related concepts with example patterns
        example_patterns = [
            f"An example of {concept} is {related_concept}",
            f"{concept} can be seen in {related_concept}",
            f"{concept} is demonstrated by {related_concept}",
            f"{concept} is illustrated by {related_concept}",
            f"{concept} is shown in {related_concept}"
        ]
        
        for pattern in example_patterns:
            for related_concept in related_concepts:
                option = pattern.format(concept=concept, related_concept=related_concept)
                # Remove any prepended numbers
                option = re.sub(r'^\d+\s+', '', option)
                options.append(option)
        
        return options

    def _generate_sentence_questions(self, sentences: List[str], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate questions from important sentences."""
        questions = []
        
        for sentence in sentences:
            if len(questions) >= count:
                break
            
            # Create a question about the sentence
            question_text = f"Which of the following statements is true about the content?"
            
            # Create options based on the sentence and its variations
            correct_option = re.sub(r'^\d+\s+', '', sentence)  # Remove any prepended numbers
            other_options = self._generate_sentence_options(sentence, sentences)
            
            if not other_options:
                continue
            
            options = [correct_option] + other_options[:3]
            random.shuffle(options)
            
            # Store the correct answer as a letter (A, B, C, D)
            correct_answer = chr(65 + options.index(correct_option))
            
            question = QuestionCreateSchema(
                question_text=question_text,
                question_type="multiple_choice",
                options=options,
                correct_answer=correct_answer,
                difficulty="medium",
                chapter_id=chapter.id
            )
            questions.append(question)
        
        return questions

    def _generate_sentence_options(self, sentence: str, all_sentences: List[str]) -> List[str]:
        """Generate plausible but incorrect options for a sentence-based question."""
        options = []
        
        # Get other sentences as potential options
        other_sentences = [s for s in all_sentences if s != sentence]
        
        # Create variations of the original sentence
        variations = [
            sentence.replace("is", "is not"),
            sentence.replace("are", "are not"),
            sentence.replace("can", "cannot"),
            sentence.replace("will", "will not"),
            sentence.replace("should", "should not"),
            sentence.replace("must", "must not"),
            sentence.replace("always", "never"),
            sentence.replace("never", "always"),
            sentence.replace("all", "none"),
            sentence.replace("none", "all")
        ]
        
        # Add variations that make sense
        for variation in variations:
            if variation != sentence and len(variation.split()) > 3:
                # Remove any prepended numbers
                variation = re.sub(r'^\d+\s+', '', variation)
                options.append(variation)
        
        # Add other sentences that are different enough
        for other in other_sentences:
            if len(other.split()) > 3 and other not in options:
                # Remove any prepended numbers
                other = re.sub(r'^\d+\s+', '', other)
                options.append(other)
        
        return options[:3]  # Return at most 3 options