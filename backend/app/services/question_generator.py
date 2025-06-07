from typing import List, Dict, Any, Tuple
from typing import List, Dict, Any, Tuple
import logging
import random
import re
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from app.models import Chapter, Question
from app.schemas import QuestionCreateSchema
import aiohttp
import nltk
from app.core.nltk_setup import download_nltk_data

logger = logging.getLogger(__name__)

class QuestionGenerator:
    def __init__(self):
        logger.info("Initializing QuestionGenerator")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        try:
            # Download required NLTK data
            download_nltk_data()
            
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Successfully loaded SentenceTransformer model")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

        # Language learning domain patterns
        self.language_domain_patterns = {
            'vocabulary': {
                'definition': [
                    "What is the meaning of the word '{word}'?",
                    "Which of the following best defines '{word}'?",
                    "What does '{word}' mean in this context?"
                ],
                'synonym': [
                    "Which word is a synonym of '{word}'?",
                    "Which of the following means the same as '{word}'?",
                    "What is another word for '{word}'?"
                ],
                'antonym': [
                    "Which word is an antonym of '{word}'?",
                    "Which of the following is the opposite of '{word}'?",
                    "What is the opposite meaning of '{word}'?"
                ],
                'usage': [
                    "In which sentence is '{word}' used correctly?",
                    "Which of the following uses '{word}' appropriately?",
                    "How should '{word}' be used in a sentence?"
                ]
            },
            'grammar': {
                'structure': [
                    "Which sentence has the correct grammar structure?",
                    "Which of the following is grammatically correct?",
                    "What is the correct way to form this sentence?"
                ],
                'tenses': [
                    "Which tense is used in this sentence?",
                    "What is the correct tense for this situation?",
                    "How should this sentence be written in the past tense?"
                ],
                'parts_of_speech': [
                    "What part of speech is '{word}' in this sentence?",
                    "Which word in this sentence is a {part_of_speech}?",
                    "How is '{word}' functioning in this sentence?"
                ]
            },
            'reading_comprehension': {
                'main_idea': [
                    "What is the main idea of this passage?",
                    "Which statement best summarizes the text?",
                    "What is the author's primary point?"
                ],
                'details': [
                    "According to the passage, what is true about {topic}?",
                    "Which detail from the text supports this idea?",
                    "What does the passage say about {topic}?"
                ],
                'inference': [
                    "What can be inferred from this passage?",
                    "Based on the text, what would the author likely agree with?",
                    "What conclusion can be drawn from this information?"
                ]
            }
        }

        # Language learning quality indicators
        self.language_quality_indicators = {
            'vocabulary_accuracy': [
                'correct definition',
                'appropriate usage',
                'contextual meaning',
                'word relationships',
                'collocations'
            ],
            'grammar_correctness': [
                'sentence structure',
                'tense usage',
                'agreement',
                'punctuation',
                'word order'
            ],
            'comprehension_depth': [
                'main idea',
                'supporting details',
                'inferences',
                'context clues',
                'author\'s purpose'
            ]
        }

        # Common language learning topics and their relationships
        self.language_topic_relationships = {
            'vocabulary': ['synonyms', 'antonyms', 'collocations', 'idioms'],
            'grammar': ['tenses', 'parts of speech', 'sentence structure', 'agreement'],
            'reading': ['comprehension', 'inference', 'context', 'main idea'],
            'writing': ['organization', 'coherence', 'style', 'tone'],
            'listening': ['comprehension', 'note-taking', 'inference', 'context'],
            'speaking': ['pronunciation', 'fluency', 'intonation', 'pragmatics']
        }

        # External resource integration
        self.external_resources = {
            'dictionary_api': 'https://api.dictionaryapi.dev/api/v2/entries/en/',
            'thesaurus_api': 'https://api.datamuse.com/words',
            'grammar_check_api': 'https://api.languagetool.org/v2/check',
            'translation_api': 'https://translation.googleapis.com/language/translate/v2'
        }

        # Domain-specific knowledge patterns for computer science
        self.cs_domain_patterns = {
            'algorithms': {
                'complexity': [
                    "What is the time complexity of {algorithm}?",
                    "Which of the following best describes the space complexity of {algorithm}?",
                    "How does the performance of {algorithm} scale with input size?"
                ],
                'implementation': [
                    "Which data structure would be most efficient for implementing {algorithm}?",
                    "What is the key step in the {algorithm} algorithm?",
                    "Which optimization would improve the performance of {algorithm}?"
                ],
                'comparison': [
                    "How does {algorithm1} compare to {algorithm2} in terms of efficiency?",
                    "When would you choose {algorithm1} over {algorithm2}?",
                    "What is the main advantage of {algorithm1} compared to {algorithm2}?"
                ]
            },
            'data_structures': {
                'operations': [
                    "What is the time complexity of {operation} in {structure}?",
                    "Which operation in {structure} has O(1) time complexity?",
                    "How would you implement {operation} in {structure}?"
                ],
                'use_cases': [
                    "When would you choose {structure1} over {structure2}?",
                    "Which data structure is most suitable for {scenario}?",
                    "What are the advantages of using {structure} for {purpose}?"
                ],
                'implementation': [
                    "How would you implement {structure} using {language}?",
                    "What are the key components of {structure}?",
                    "Which design pattern would be most appropriate for {structure}?"
                ]
            },
            'programming_concepts': {
                'principles': [
                    "Which principle of {concept} is demonstrated in this code?",
                    "How does {concept} improve code maintainability?",
                    "What is the main benefit of applying {concept}?"
                ],
                'best_practices': [
                    "Which of the following is a best practice for {concept}?",
                    "How would you refactor this code to better follow {concept}?",
                    "What is the recommended approach for implementing {concept}?"
                ],
                'common_pitfalls': [
                    "Which of these is a common mistake when using {concept}?",
                    "What could go wrong if {concept} is not properly implemented?",
                    "Which scenario would cause issues with {concept}?"
                ]
            }
        }

        # Quality indicators for computer science questions
        self.cs_quality_indicators = {
            'technical_accuracy': [
                'time complexity',
                'space complexity',
                'algorithm efficiency',
                'data structure operations',
                'implementation details'
            ],
            'practical_relevance': [
                'real-world application',
                'use case',
                'scenario',
                'problem-solving',
                'optimization'
            ],
            'conceptual_understanding': [
                'principles',
                'fundamentals',
                'core concepts',
                'underlying mechanisms',
                'theoretical basis'
            ]
        }

        # Common computer science topics and their relationships
        self.cs_topic_relationships = {
            'algorithms': ['data structures', 'complexity analysis', 'optimization'],
            'data structures': ['algorithms', 'memory management', 'performance'],
            'object-oriented': ['inheritance', 'polymorphism', 'encapsulation'],
            'databases': ['normalization', 'indexing', 'transactions'],
            'networking': ['protocols', 'routing', 'security'],
            'operating systems': ['processes', 'memory', 'scheduling']
        }

        # Domain-specific question patterns
        self.domain_patterns = {
            'concept': {
                'definition': [
                    "What is the definition of {concept}?",
                    "Which of the following best describes {concept}?",
                    "What does {concept} refer to in this context?"
                ],
                'application': [
                    "How would you apply {concept} in a real-world scenario?",
                    "Which situation best demonstrates the use of {concept}?",
                    "In what context would {concept} be most relevant?"
                ],
                'analysis': [
                    "What are the key components of {concept}?",
                    "How does {concept} relate to {related_concept}?",
                    "What are the implications of {concept}?"
                ]
            },
            'relationship': {
                'causal': [
                    "What is the relationship between {concept1} and {concept2}?",
                    "How does {concept1} affect {concept2}?",
                    "What happens to {concept2} when {concept1} changes?",
                    "Which statement best describes how {concept1} influences {concept2}?"
                ],
                'comparative': [
                    "How does {concept1} differ from {concept2}?",
                    "What are the similarities between {concept1} and {concept2}?",
                    "Which statement best compares {concept1} and {concept2}?",
                    "What distinguishes {concept1} from {concept2}?"
                ],
                'hierarchical': [
                    "Which of the following is a subset of {concept1}?",
                    "What category does {concept1} belong to?",
                    "How is {concept1} classified in relation to {concept2}?",
                    "Which statement best describes the hierarchy between {concept1} and {concept2}?"
                ]
            },
            'application': {
                'problem_solving': [
                    "How would you solve this problem using {concept}?",
                    "Which approach would be most effective for this scenario?",
                    "What steps would you take to apply {concept} here?",
                    "How would you use {concept} to address this situation?"
                ],
                'evaluation': [
                    "Which solution best demonstrates the principles of {concept}?",
                    "How would you evaluate the effectiveness of {concept} in this case?",
                    "What criteria would you use to assess the application of {concept}?",
                    "Which approach best exemplifies the use of {concept}?"
                ],
                'synthesis': [
                    "How would you combine {concept1} and {concept2} to solve this problem?",
                    "What new insights can be gained by applying {concept} in this context?",
                    "How would you integrate {concept} with existing knowledge?",
                    "Which approach best synthesizes {concept1} and {concept2}?"
                ]
            }
        }
        
        # Domain-specific difficulty indicators
        self.difficulty_indicators = {
            'easy': {
                'keywords': ['define', 'identify', 'list', 'describe', 'explain'],
                'complexity': 'basic understanding'
            },
            'medium': {
                'keywords': ['compare', 'contrast', 'analyze', 'apply', 'evaluate'],
                'complexity': 'application and analysis'
            },
            'hard': {
                'keywords': ['synthesize', 'create', 'design', 'critique', 'justify'],
                'complexity': 'synthesis and evaluation'
            }
        }

        # Domain detection patterns
        self.domain_indicators = {
            'computer_science': [
                'algorithm', 'data structure', 'programming', 'software',
                'database', 'network', 'security', 'web development'
            ],
            'language_learning': [
                'vocabulary', 'grammar', 'reading', 'writing',
                'pronunciation', 'speaking', 'listening'
            ],
            'mathematics': [
                'algebra', 'calculus', 'geometry', 'statistics',
                'equation', 'function', 'theorem', 'proof'
            ],
            'science': [
                'physics', 'chemistry', 'biology', 'experiment',
                'theory', 'hypothesis', 'research', 'analysis'
            ],
            'history': [
                'period', 'era', 'century', 'event',
                'civilization', 'culture', 'war', 'revolution'
            ],
            'business': [
                'management', 'marketing', 'finance', 'economics',
                'strategy', 'organization', 'leadership', 'entrepreneurship'
            ]
        }

        # Generic question patterns for any domain
        self.generic_domain_patterns = {
            'concept': {
                'definition': [
                    "What is the definition of {concept}?",
                    "Which of the following best describes {concept}?",
                    "What does {concept} refer to in this context?"
                ],
                'application': [
                    "How would you apply {concept} in a real-world scenario?",
                    "Which situation best demonstrates the use of {concept}?",
                    "In what context would {concept} be most relevant?"
                ],
                'analysis': [
                    "What are the key components of {concept}?",
                    "How does {concept} relate to {related_concept}?",
                    "What are the implications of {concept}?"
                ]
            },
            'process': {
                'steps': [
                    "What is the correct sequence of steps for {process}?",
                    "Which step comes first in {process}?",
                    "What is the final step in {process}?"
                ],
                'purpose': [
                    "What is the main purpose of {process}?",
                    "Why is {process} important?",
                    "What problem does {process} solve?"
                ],
                'evaluation': [
                    "How would you evaluate the effectiveness of {process}?",
                    "What criteria would you use to assess {process}?",
                    "How can you measure the success of {process}?"
                ]
            },
            'analysis': {
                'comparison': [
                    "How does {concept1} compare to {concept2}?",
                    "What are the similarities between {concept1} and {concept2}?",
                    "What are the key differences between {concept1} and {concept2}?"
                ],
                'evaluation': [
                    "What are the strengths and weaknesses of {concept}?",
                    "How effective is {concept} in achieving its goals?",
                    "What are the limitations of {concept}?"
                ],
                'synthesis': [
                    "How would you combine {concept1} and {concept2} to solve this problem?",
                    "What new insights can be gained by applying {concept} in this context?",
                    "How would you integrate {concept} with existing knowledge?"
                ]
            }
        }

    async def _fetch_external_resources(self, word: str) -> Dict[str, Any]:
        """Fetch additional information from external resources."""
        try:
            # Fetch from dictionary API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.external_resources['dictionary_api']}{word}") as response:
                    if response.status == 200:
                        dictionary_data = await response.json()
                    else:
                        dictionary_data = None

                # Fetch from thesaurus API
                async with session.get(f"{self.external_resources['thesaurus_api']}?ml={word}") as response:
                    if response.status == 200:
                        thesaurus_data = await response.json()
                    else:
                        thesaurus_data = None

            return {
                'dictionary': dictionary_data,
                'thesaurus': thesaurus_data
            }
        except Exception as e:
            logger.error(f"Error fetching external resources: {str(e)}")
            return {}

    async def _generate_language_questions(self, content: str, analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate language learning questions."""
        questions = []
        
        try:
            logger.info("Starting language question generation")
            
            # Extract vocabulary words
            vocabulary = self._extract_vocabulary(content)
            logger.info(f"Extracted {len(vocabulary)} vocabulary words")
            
            if vocabulary:
                # Generate vocabulary questions
                vocab_questions = await self._generate_vocabulary_questions(
                    vocabulary,
                    analysis,
                    count // 3,
                    chapter
                )
                logger.info(f"Generated {len(vocab_questions)} vocabulary questions")
                questions.extend(vocab_questions)
            
            # Extract grammar structures
            grammar_structures = self._extract_grammar_structures(content)
            logger.info(f"Extracted {len(grammar_structures)} grammar structures")
            
            if grammar_structures:
                # Generate grammar questions
                grammar_questions = self._generate_grammar_questions(
                    grammar_structures,
                    analysis,
                    count // 3,
                    chapter
                )
                logger.info(f"Generated {len(grammar_questions)} grammar questions")
                questions.extend(grammar_questions)
            
            # Extract reading passages
            reading_passages = self._extract_reading_passages(content)
            logger.info(f"Extracted {len(reading_passages)} reading passages")
            
            if reading_passages:
                # Generate reading comprehension questions
                reading_questions = self._generate_reading_questions(
                    reading_passages,
                    analysis,
                    count // 3,
                    chapter
                )
                logger.info(f"Generated {len(reading_questions)} reading questions")
                questions.extend(reading_questions)
            
            # If no specific questions were generated, create basic language questions
            if not questions:
                logger.info("No specific language questions generated, creating basic language questions")
                questions = self._generate_basic_language_questions(content, count, chapter)
                logger.info(f"Generated {len(questions)} basic language questions")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error in _generate_language_questions: {str(e)}", exc_info=True)
            return []

    def _extract_vocabulary(self, content: str) -> List[Dict[str, Any]]:
        """Extract vocabulary words and their context."""
        vocabulary = []
        
        try:
            # Use NLTK for word extraction
            words = nltk.word_tokenize(content)
            pos_tags = nltk.pos_tag(words)
            
            for word, tag in pos_tags:
                if tag.startswith(('NN', 'VB', 'JJ', 'RB')):  # Nouns, verbs, adjectives, adverbs
                    # Get word context (surrounding words)
                    word_index = words.index(word)
                    start = max(0, word_index - 5)
                    end = min(len(words), word_index + 6)
                    context = ' '.join(words[start:end])
                    
                    vocabulary.append({
                        'word': word,
                        'pos': tag,
                        'context': context
                    })
        except Exception as e:
            logger.error(f"Error extracting vocabulary: {str(e)}")
            # Fallback to simple word extraction
            words = content.split()
            for word in words:
                if len(word) > 3:  # Only consider words longer than 3 characters
                    vocabulary.append({
                        'word': word,
                        'pos': 'UNKNOWN',
                        'context': word
                    })
        
        return vocabulary

    def _extract_grammar_structures(self, content: str) -> List[Dict[str, Any]]:
        """Extract grammar structures from content."""
        structures = []
        
        # Use NLTK for sentence parsing
        sentences = nltk.sent_tokenize(content)
        
        for sentence in sentences:
            # Parse sentence structure
            tree = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)))
            
            # Extract grammar patterns
            patterns = self._extract_grammar_patterns(tree)
            
            structures.append({
                'sentence': sentence,
                'patterns': patterns
            })
        
        return structures

    def _extract_grammar_patterns(self, tree) -> List[Dict[str, Any]]:
        """Extract grammar patterns from a parsed sentence tree."""
        patterns = []
        
        try:
            # Extract basic sentence structure
            if isinstance(tree, nltk.Tree):
                # Get the top-level structure
                pattern = {
                    'type': tree.label(),
                    'structure': [],
                    'words': []
                }
                
                # Extract words and their parts of speech
                for subtree in tree:
                    if isinstance(subtree, nltk.Tree):
                        pattern['structure'].append(subtree.label())
                        # Get words from leaf nodes
                        for leaf in subtree.leaves():
                            pattern['words'].append(leaf)
                    else:
                        pattern['words'].append(subtree)
                
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error extracting grammar patterns: {str(e)}")
            # Return a simple pattern if extraction fails
            return [{
                'type': 'S',
                'structure': ['NP', 'VP'],
                'words': []
            }]

    def _extract_reading_passages(self, content: str) -> List[Dict[str, Any]]:
        """Extract reading passages for comprehension questions."""
        passages = []
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            if len(paragraph.split()) > 50:  # Only use substantial paragraphs
                passages.append({
                    'text': paragraph,
                    'main_idea': self._extract_main_idea(paragraph),
                    'key_points': self._extract_key_points(paragraph)
                })
        
        return passages

    async def _generate_vocabulary_questions(self, vocabulary: List[Dict[str, Any]], analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate vocabulary questions."""
        questions = []
        
        for word_data in vocabulary[:count]:
            word = word_data['word']
            
            # Get external resources for the word
            external_data = await self._fetch_external_resources(word)
            
            # Generate different types of vocabulary questions
            question_types = ['definition', 'synonym', 'antonym', 'usage']
            
            for q_type in question_types:
                if len(questions) >= count:
                    break
                
                # Get question pattern
                pattern = random.choice(self.language_domain_patterns['vocabulary'][q_type])
                question_text = pattern.format(word=word)
                
                # Generate options based on external data
                options = self._generate_vocabulary_options(word, q_type, external_data)
                
                if len(options) >= 4:
                    # Convert options to letter format
                    letter_options = {chr(65 + i): opt for i, opt in enumerate(options)}  # A, B, C, D
                    
                    question = QuestionCreateSchema(
                        question_text=question_text,
                        question_type="multiple_choice",
                        options=letter_options,
                        correct_answer='A',  # First option is always correct
                        difficulty=self._determine_language_difficulty(q_type),
                        chapter_id=chapter.id
                    )
                    questions.append(question)
            
            return questions

    def _generate_vocabulary_options(self, word: str, q_type: str, external_data: Dict[str, Any]) -> List[str]:
        """Generate options for vocabulary questions."""
        options = []
        
        try:
            if q_type == 'definition':
                # Get definitions from external data
                if external_data.get('dictionary'):
                    definitions = [meaning['definition'] for meaning in external_data['dictionary'][0]['meanings'][0]['definitions']]
                    options.extend(definitions[:3])  # Use up to 3 definitions
                
                # If not enough definitions, add some generic ones
                while len(options) < 4:
                    options.append(f"A word related to {word}")
            
            elif q_type == 'synonym':
                # Get synonyms from external data
                if external_data.get('thesaurus'):
                    synonyms = [syn['word'] for syn in external_data['thesaurus'] if syn['word'] != word]
                    options.extend(synonyms[:3])  # Use up to 3 synonyms
                
                # If not enough synonyms, add some generic ones
                while len(options) < 4:
                    options.append(f"Another word for {word}")
            
            elif q_type == 'antonym':
                # Get antonyms from external data
                if external_data.get('dictionary'):
                    antonyms = []
                    for meaning in external_data['dictionary'][0]['meanings']:
                        if 'antonyms' in meaning:
                            antonyms.extend(meaning['antonyms'])
                    options.extend(antonyms[:3])  # Use up to 3 antonyms
                
                # If not enough antonyms, add some generic ones
                while len(options) < 4:
                    options.append(f"Opposite of {word}")
            
            else:  # usage
                # Generate example sentences
                if external_data.get('dictionary'):
                    examples = [meaning['example'] for meaning in external_data['dictionary'][0]['meanings'] if 'example' in meaning]
                    options.extend(examples[:3])  # Use up to 3 examples
                
                # If not enough examples, add some generic ones
                while len(options) < 4:
                    options.append(f"Example sentence using {word}")
            
            # Ensure we have exactly 4 options
            if len(options) > 4:
                options = options[:4]
            elif len(options) < 4:
                # Add more generic options if needed
                generic_options = [
                    f"Option related to {word}",
                    f"Another option for {word}",
                    f"Different usage of {word}",
                    f"Alternative meaning of {word}"
                ]
                options.extend(generic_options[:4 - len(options)])
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating vocabulary options: {str(e)}")
            # Return generic options if external data fails
            return [
                f"Definition of {word}",
                f"Synonym of {word}",
                f"Antonym of {word}",
                f"Usage of {word}"
            ]

    def _generate_grammar_questions(self, structures: List[Dict[str, Any]], analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate grammar questions."""
        questions = []
        
        for structure in structures[:count]:
            sentence = structure['sentence']
            patterns = structure['patterns']
            
            # Generate different types of grammar questions
            question_types = ['structure', 'tenses', 'parts_of_speech']
            
            for q_type in question_types:
                if len(questions) >= count:
                    break
                
                # Get question pattern
                pattern = random.choice(self.language_domain_patterns['grammar'][q_type])
                
                if q_type == 'parts_of_speech':
                    # Select a word from the sentence
                    words = nltk.word_tokenize(sentence)
                    word = random.choice(words)
                    pos = nltk.pos_tag([word])[0][1]
                    question_text = pattern.format(word=word, part_of_speech=pos)
                else:
                    question_text = pattern
                
                # Generate options
                options = self._generate_grammar_options(sentence, q_type, patterns)
                
                if len(options) >= 4:
                    # Convert options to letter format
                    letter_options = {chr(65 + i): opt for i, opt in enumerate(options)}  # A, B, C, D
                    
                    question = QuestionCreateSchema(
                        question_text=question_text,
                        question_type="multiple_choice",
                        options=letter_options,
                        correct_answer='A',  # First option is always correct
                        difficulty=self._determine_language_difficulty(q_type),
                        chapter_id=chapter.id
                    )
                    questions.append(question)
        
        return questions

    def _generate_grammar_options(self, sentence: str, q_type: str, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate options for grammar questions."""
        options = []
        
        try:
            if q_type == 'structure':
                # Generate different sentence structures
                words = nltk.word_tokenize(sentence)
                pos_tags = nltk.pos_tag(words)
                
                # Original structure
                options.append(sentence)
                
                # Generate variations
                if len(words) >= 4:
                    # Change word order
                    words_copy = words.copy()
                    random.shuffle(words_copy)
                    options.append(' '.join(words_copy))
                    
                    # Change some words
                    words_copy = words.copy()
                    for i in range(len(words_copy)):
                        if random.random() < 0.3:  # 30% chance to change each word
                            words_copy[i] = f"word{i}"
                    options.append(' '.join(words_copy))
                    
                    # Add a completely different sentence
                    options.append("This is a different sentence structure.")
            
            elif q_type == 'tenses':
                # Generate different tense variations
                options.append(sentence)  # Original tense
                
                # Past tense
                words = nltk.word_tokenize(sentence)
                pos_tags = nltk.pos_tag(words)
                past_words = []
                for word, tag in pos_tags:
                    if tag.startswith('VB'):  # Verb
                        past_words.append(f"past_{word}")
                    else:
                        past_words.append(word)
                options.append(' '.join(past_words))
                
                # Future tense
                future_words = []
                for word, tag in pos_tags:
                    if tag.startswith('VB'):  # Verb
                        future_words.append(f"will_{word}")
                    else:
                        future_words.append(word)
                options.append(' '.join(future_words))
                
                # Add a completely different tense
                options.append("This is a different tense.")
            
            else:  # parts_of_speech
                # Generate different parts of speech
                words = nltk.word_tokenize(sentence)
                pos_tags = nltk.pos_tag(words)
                
                # Original
                options.append(sentence)
                
                # Change some parts of speech
                words_copy = words.copy()
                for i, (word, tag) in enumerate(pos_tags):
                    if random.random() < 0.3:  # 30% chance to change each word
                        if tag.startswith('NN'):  # Noun
                            words_copy[i] = f"noun{i}"
                        elif tag.startswith('VB'):  # Verb
                            words_copy[i] = f"verb{i}"
                        elif tag.startswith('JJ'):  # Adjective
                            words_copy[i] = f"adj{i}"
                options.append(' '.join(words_copy))
                
                # Add more variations
                options.append("This is a different part of speech.")
                options.append("Another part of speech variation.")
            
            # Ensure we have exactly 4 options
            if len(options) > 4:
                options = options[:4]
            elif len(options) < 4:
                # Add more generic options if needed
                generic_options = [
                    "Generic grammar option 1",
                    "Generic grammar option 2",
                    "Generic grammar option 3",
                    "Generic grammar option 4"
                ]
                options.extend(generic_options[:4 - len(options)])
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating grammar options: {str(e)}")
            # Return generic options if generation fails
            return [
                "Original sentence",
                "Modified sentence 1",
                "Modified sentence 2",
                "Modified sentence 3"
            ]

    def _generate_reading_questions(self, passages: List[Dict[str, Any]], analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate reading comprehension questions."""
        questions = []
        
        for passage in passages[:count]:
            # Generate different types of reading questions
            question_types = ['main_idea', 'details', 'inference']
            
            for q_type in question_types:
                if len(questions) >= count:
                    break
                
                # Get question pattern
                pattern = random.choice(self.language_domain_patterns['reading_comprehension'][q_type])
                
                if q_type == 'details':
                    # Select a topic from key points
                    topic = random.choice(passage['key_points'])
                    question_text = pattern.format(topic=topic)
                else:
                    question_text = pattern
                
                # Generate options
                options = self._generate_reading_options(passage, q_type)
                
                if len(options) >= 4:
                    # Convert options to letter format
                    letter_options = {chr(65 + i): opt for i, opt in enumerate(options)}  # A, B, C, D
                    
                    question = QuestionCreateSchema(
                        question_text=question_text,
                        question_type="multiple_choice",
                        options=letter_options,
                        correct_answer='A',  # First option is always correct
                        difficulty=self._determine_language_difficulty(q_type),
                        chapter_id=chapter.id
                    )
                    questions.append(question)
        
        return questions

    def _generate_reading_options(self, passage: Dict[str, Any], q_type: str) -> List[str]:
        """Generate options for reading comprehension questions."""
        options = []
        
        try:
            if q_type == 'main_idea':
                # Use the main idea as correct answer
                options.append(passage['main_idea'])
                
                # Generate plausible alternatives
                sentences = nltk.sent_tokenize(passage['text'])
                other_sentences = [s for s in sentences if s != passage['main_idea']]
                options.extend(random.sample(other_sentences, min(3, len(other_sentences))))
            
            elif q_type == 'details':
                # Use key points as options
                options.extend(passage['key_points'][:4])
            
            else:  # inference
                # Generate inference-based options
                main_idea = passage['main_idea']
                options.append(f"Based on the text, {main_idea}")
                
                # Generate plausible alternatives
                sentences = nltk.sent_tokenize(passage['text'])
                other_sentences = [s for s in sentences if s != main_idea]
                for sentence in other_sentences[:3]:
                    options.append(f"Based on the text, {sentence}")
            
            # Ensure we have exactly 4 options
            if len(options) > 4:
                options = options[:4]
            elif len(options) < 4:
                # Add more generic options if needed
                generic_options = [
                    "Generic reading option 1",
                    "Generic reading option 2",
                    "Generic reading option 3",
                    "Generic reading option 4"
                ]
                options.extend(generic_options[:4 - len(options)])
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating reading options: {str(e)}")
            # Return generic options if generation fails
            return [
                "Main idea of the passage",
                "Key detail from the passage",
                "Inference from the passage",
                "Alternative interpretation"
            ]

    def _determine_language_difficulty(self, question_type: str) -> str:
        """Determine difficulty level for language questions."""
        difficulty_map = {
            'definition': 'easy',
            'synonym': 'medium',
            'antonym': 'medium',
            'usage': 'hard',
            'structure': 'medium',
            'tenses': 'hard',
            'parts_of_speech': 'medium',
            'main_idea': 'easy',
            'details': 'medium',
            'inference': 'hard'
        }
        return difficulty_map.get(question_type, 'medium')

    async def generate_questions(self, chapter: Chapter, num_questions: int = 5) -> List[QuestionCreateSchema]:
        """Generate questions based on content domain."""
        try:
            # Analyze content
            content_analysis = self._analyze_content(chapter.content)
            if not content_analysis:
                logger.warning("No content analysis available")
                return []
            
            # Detect domain(s)
            domains = self._detect_domain(chapter.content)
            logger.info(f"Detected domains: {domains}")
            
            questions = []
            
            if not domains:
                # If no specific domain is detected, use generic patterns
                logger.info("No specific domains detected, using generic patterns")
                questions = self._generate_generic_questions(content_analysis, num_questions, chapter)
            else:
                # Generate domain-specific questions
                questions_per_domain = max(1, num_questions // len(domains))
                for domain in domains:
                    try:
                        if domain == 'language_learning':
                            # Handle language learning questions asynchronously
                            domain_questions = await self._generate_language_questions(
                                chapter.content,
                                content_analysis,
                                questions_per_domain,
                                chapter
                            )
                        else:
                            # Handle other domains
                            domain_questions = await self._generate_domain_questions(
                                domain,
                                chapter.content,
                                content_analysis,
                                questions_per_domain,
                                chapter
                            )
                        
                        if domain_questions:
                            questions.extend(domain_questions)
                        else:
                            logger.warning(f"No questions generated for domain: {domain}")
                    except Exception as e:
                        logger.error(f"Error generating questions for domain {domain}: {str(e)}")
                        continue
            
            # If no domain-specific questions were generated, fall back to generic questions
            if not questions:
                logger.warning("No domain-specific questions generated, falling back to generic questions")
                questions = self._generate_generic_questions(content_analysis, num_questions, chapter)
            
            # If still no questions, generate very basic questions from the content
            if not questions:
                logger.warning("No questions generated with any method, creating basic questions")
                questions = self._generate_basic_questions(chapter.content, num_questions, chapter)
            
            # Shuffle and return questions
            random.shuffle(questions)
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}", exc_info=True)
            raise

    def _generate_basic_language_questions(self, content: str, count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate basic language learning questions when specific methods fail."""
        questions = []
        try:
            # Split content into sentences
            sentences = nltk.sent_tokenize(content)
            
            for sentence in sentences[:count]:
                if len(sentence.split()) < 5:  # Skip very short sentences
                    continue
                
                # Create different types of basic language questions
                question_types = [
                    (f"What is the main idea of this sentence: '{sentence}'?", "comprehension"),
                    (f"Which word in this sentence is a noun: '{sentence}'?", "grammar"),
                    (f"What is the meaning of this sentence: '{sentence}'?", "vocabulary")
                ]
                
                for question_text, q_type in question_types:
                    # Generate options
                    options = []
                    
                    if q_type == "comprehension":
                        # For comprehension, use other sentences as options
                        options = [sentence]  # Correct answer
                        other_sentences = [s for s in sentences if s != sentence]
                        options.extend(random.sample(other_sentences, min(3, len(other_sentences))))
                    elif q_type == "grammar":
                        # For grammar, use different parts of speech as options
                        words = nltk.word_tokenize(sentence)
                        pos_tags = nltk.pos_tag(words)
                        nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
                        if nouns:
                            options = [nouns[0]]  # Correct answer
                            other_words = [word for word in words if word not in nouns]
                            options.extend(random.sample(other_words, min(3, len(other_words))))
                    else:  # vocabulary
                        # For vocabulary, use different words as options
                        words = nltk.word_tokenize(sentence)
                        if len(words) >= 4:
                            options = [words[0]]  # Correct answer
                            options.extend(random.sample(words[1:], min(3, len(words) - 1)))
                    
                    if len(options) >= 4:
                        # Convert options to letter format
                        letter_options = {chr(65 + i): opt for i, opt in enumerate(options)}  # A, B, C, D
                        correct_letter = 'A'  # First option is always correct
                        
                        question = QuestionCreateSchema(
                            question_text=question_text,
                            question_type="multiple_choice",
                            options=letter_options,
                            correct_answer=correct_letter,
                            difficulty="medium",
                            chapter_id=chapter.id
                        )
                        questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating basic language questions: {str(e)}")
            return []

    def _detect_domain(self, content: str) -> List[str]:
        """Detect the domain(s) of the content."""
        detected_domains = []
        content_lower = content.lower()
        
        for domain, indicators in self.domain_indicators.items():
            # Count how many indicators are present in the content
            indicator_count = sum(1 for indicator in indicators if indicator in content_lower)
            
            # If more than 2 indicators are found, consider it part of this domain
            if indicator_count >= 2:
                detected_domains.append(domain)
        
        return detected_domains

    def _extract_domain_concepts(self, content: str, domain: str) -> List[Dict[str, Any]]:
        """Extract domain-specific concepts from content."""
        concepts = []
        
        # Use NLTK for basic NLP
        sentences = nltk.sent_tokenize(content)
        
        for sentence in sentences:
            # Extract noun phrases and key terms
            words = nltk.word_tokenize(sentence)
            pos_tags = nltk.pos_tag(words)
            
            # Extract concepts based on domain
            if domain == 'computer_science':
                concepts.extend(self._extract_cs_concepts(sentence, pos_tags))
            elif domain == 'language_learning':
                concepts.extend(self._extract_language_concepts(sentence, pos_tags))
            elif domain == 'mathematics':
                concepts.extend(self._extract_math_concepts(sentence, pos_tags))
            elif domain == 'science':
                concepts.extend(self._extract_science_concepts(sentence, pos_tags))
            elif domain == 'history':
                concepts.extend(self._extract_history_concepts(sentence, pos_tags))
            elif domain == 'business':
                concepts.extend(self._extract_business_concepts(sentence, pos_tags))
            else:
                # Generic concept extraction
                concepts.extend(self._extract_generic_concepts(sentence, pos_tags))
        
        return concepts

    def _extract_generic_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract generic concepts from a sentence."""
        concepts = []
        
        # Look for noun phrases and important terms
        for i, (word, tag) in enumerate(pos_tags):
            if tag.startswith(('NN', 'JJ')):  # Nouns and adjectives
                # Get context (surrounding words)
                start = max(0, i - 2)
                end = min(len(pos_tags), i + 3)
                context = ' '.join(w for w, _ in pos_tags[start:end])
                
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': context,
                    'sentence': sentence
                })
        
        return concepts

    def _generate_generic_questions(self, analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate generic questions using universal patterns."""
        questions = []
        
        try:
            logger.info("Starting generic question generation")
            
            # Extract concepts
            concepts = self._extract_generic_concepts(
                ' '.join(analysis.get('important_sentences', [])),
                nltk.pos_tag(nltk.word_tokenize(' '.join(analysis.get('important_sentences', []))))
            )
            
            logger.info(f"Extracted {len(concepts)} concepts for generic questions")
            
            if not concepts:
                logger.warning("No concepts found for generic questions")
                return []
            
            # Generate questions for each concept
            for concept in concepts[:count]:
                try:
                    # Select question type
                    question_type = random.choice(['concept', 'relationship', 'application'])
                    pattern_category = random.choice(list(self.generic_domain_patterns[question_type].keys()))
                    
                    logger.info(f"Generating question for concept '{concept.get('term', 'unknown')}' with type '{question_type}' and category '{pattern_category}'")
                    
                    # Get question pattern
                    pattern = random.choice(self.generic_domain_patterns[question_type][pattern_category])
                    
                    # Format question
                    if pattern_category in ['comparison', 'evaluation', 'synthesis']:
                        # Find a related concept
                        other_concepts = [c for c in concepts if c['term'] != concept['term']]
                        if not other_concepts:
                            logger.warning(f"No related concepts found for '{concept.get('term', 'unknown')}'")
                            continue
                        related_concept = random.choice(other_concepts)
                        question_text = pattern.format(
                            concept1=concept['term'],
                            concept2=related_concept['term']
                        )
                    else:
                        question_text = pattern.format(concept=concept['term'])
                    
                    # Generate options
                    options = self._generate_generic_options(concept, pattern_category, concepts)
                    logger.info(f"Generated {len(options)} options for question")
                    
                    if len(options) >= 4:
                        question = QuestionCreateSchema(
                            question_text=question_text,
                            question_type="multiple_choice",
                            options=options,  # Pass as list
                            correct_answer='A',  # First option is always correct
                            difficulty=self._determine_difficulty(question_text, pattern_category),
                            chapter_id=chapter.id
                        )
                        questions.append(question)
                        logger.info(f"Successfully created question: {question_text}")
                except Exception as e:
                    logger.error(f"Error generating generic question for concept {concept.get('term', 'unknown')}: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"Generated {len(questions)} generic questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error in _generate_generic_questions: {str(e)}", exc_info=True)
            return []

    def _generate_generic_options(self, concept: Dict[str, Any], pattern_category: str, all_concepts: List[Dict[str, Any]]) -> List[str]:
        """Generate generic options for questions."""
        options = []
        
        # Add correct answer
        if pattern_category == 'definition':
            correct_answer = concept['sentence']
        elif pattern_category == 'application':
            correct_answer = f"Using {concept['term']} in {concept['context']}"
        else:
            correct_answer = f"Analysis of {concept['term']} in {concept['context']}"
        
        options.append(correct_answer)
        
        # Generate plausible incorrect options
        other_concepts = [c for c in all_concepts if c['term'] != concept['term']]
        other_options = []
        
        for other in other_concepts[:3]:
            if pattern_category == 'definition':
                other_options.append(other['sentence'])
            elif pattern_category == 'application':
                other_options.append(f"Using {other['term']} in {other['context']}")
            else:
                other_options.append(f"Analysis of {other['term']} in {other['context']}")
        
        options.extend(other_options)
        return options

    async def _generate_domain_questions(self, domain: str, content: str, analysis: Dict[str, Any], count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate domain-specific questions."""
        questions = []
        
        # Extract domain-specific concepts
        domain_concepts = self._extract_domain_concepts(content, domain)
        
        if not domain_concepts:
            logger.warning(f"No domain concepts found for domain: {domain}")
            return []
        
        # Generate questions for each concept
        for concept in domain_concepts[:count]:
            try:
                # Select question type from available types in domain_patterns
                question_type = random.choice(['concept', 'relationship', 'application'])
                pattern_category = random.choice(list(self.domain_patterns[question_type].keys()))
                
                # Get question pattern
                pattern = random.choice(self.domain_patterns[question_type][pattern_category])
                
                # Format question
                if pattern_category in ['comparative', 'causal', 'hierarchical']:
                    # Find a related concept
                    other_concepts = [c for c in domain_concepts if c['term'] != concept['term']]
                    if not other_concepts:
                        # If no other concepts available, skip this pattern
                        continue
                    related_concept = random.choice(other_concepts)
                    question_text = pattern.format(
                        concept1=concept['term'],
                        concept2=related_concept['term']
                    )
                else:
                    question_text = pattern.format(concept=concept['term'])
                
                # Generate options
                options = self._generate_domain_options(concept, pattern_category, domain_concepts)
                
                if len(options) >= 4:
                    question = QuestionCreateSchema(
                        question_text=question_text,
                        question_type="multiple_choice",
                        options=options,
                        correct_answer='A',  # First option is always correct
                        difficulty=self._determine_difficulty(question_text, pattern_category),
                        chapter_id=chapter.id
                    )
                    questions.append(question)
            except Exception as e:
                logger.error(f"Error generating question for concept {concept.get('term', 'unknown')}: {str(e)}")
                continue
        
        return questions

    def _generate_domain_options(self, concept: Dict[str, Any], pattern_category: str, all_concepts: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate domain-specific options for questions."""
        options = {}
        
        # Add correct answer
        if pattern_category == 'definition':
            correct_answer = concept['sentence']
        elif pattern_category == 'application':
            correct_answer = f"Using {concept['term']} in {concept['context']}"
        else:
            correct_answer = f"Analysis of {concept['term']} in {concept['context']}"
        
        options['A'] = correct_answer
        
        # Generate plausible incorrect options
        other_concepts = [c for c in all_concepts if c['term'] != concept['term']]
        other_options = []
        
        for other in other_concepts[:3]:
            if pattern_category == 'definition':
                other_options.append(other['sentence'])
            elif pattern_category == 'application':
                other_options.append(f"Using {other['term']} in {other['context']}")
            else:
                other_options.append(f"Analysis of {other['term']} in {other['context']}")
        
        for i, option in enumerate(other_options[:3], 1):
            options[chr(65 + i)] = option
        
        return options

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
            'important_sentences': [],
            'cs_topics': set(),  # Add computer science specific topics
            'technical_terms': set(),  # Add technical terminology
            'code_examples': [],  # Add code examples
            'chapter_id': None  # Add chapter_id field
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
            
            # Identify computer science topics
            for topic, related_topics in self.cs_topic_relationships.items():
                if topic.lower() in section.lower():
                    analysis['cs_topics'].add(topic)
                    analysis['cs_topics'].update(related_topics)
            
            # Extract technical terms
            technical_terms = self._extract_technical_terms(section)
            analysis['technical_terms'].update(technical_terms)
            
            # Extract code examples
            code_examples = self._extract_code_examples(section)
            analysis['code_examples'].extend(code_examples)
        
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

    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms specific to computer science."""
        technical_terms = []
        
        # Common technical term patterns
        patterns = [
            r'\b(?:O\([^)]+\)|Big O|time complexity|space complexity)\b',
            r'\b(?:algorithm|data structure|design pattern|framework|library)\b',
            r'\b(?:inheritance|polymorphism|encapsulation|abstraction)\b',
            r'\b(?:database|query|index|transaction|normalization)\b',
            r'\b(?:protocol|routing|security|encryption|authentication)\b',
            r'\b(?:process|thread|memory|scheduling|synchronization)\b'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            technical_terms.extend(match.group() for match in matches)
        
        return list(set(technical_terms))

    def _extract_code_examples(self, text: str) -> List[str]:
        """Extract code examples from the text."""
        code_examples = []
        
        # Look for code blocks
        code_blocks = re.finditer(r'```(?:\w+)?\n(.*?)\n```', text, re.DOTALL)
        code_examples.extend(block.group(1) for block in code_blocks)
        
        # Look for inline code
        inline_code = re.finditer(r'`([^`]+)`', text)
        code_examples.extend(code.group(1) for code in inline_code)
        
        return code_examples

    def _determine_difficulty(self, question_text: str, pattern_type: str) -> str:
        """Determine question difficulty based on content and pattern type."""
        # Check for difficulty indicators in the question text
        for difficulty, indicators in self.difficulty_indicators.items():
            if any(keyword in question_text.lower() for keyword in indicators['keywords']):
                return difficulty
        
        # Default difficulty based on pattern type
        difficulty_map = {
            'definition': 'easy',
            'application': 'medium',
            'analysis': 'hard'
        }
        return difficulty_map.get(pattern_type, 'medium')

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text using NLTK."""
        try:
            # Download required NLTK data if not already downloaded
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            # Split text into sentences
            sentences = nltk.sent_tokenize(text)
            
            # Filter out very short sentences (likely not meaningful)
            sentences = [s.strip() for s in sentences if len(s.split()) > 3]
            
            return sentences
        except Exception as e:
            logger.error(f"Error extracting sentences: {str(e)}")
            # Fallback to simple sentence splitting if NLTK fails
            return [s.strip() for s in text.split('.') if s.strip()]

    def _extract_main_idea(self, text: str) -> str:
        """Extract the main idea from a paragraph using NLP techniques."""
        try:
            # Split into sentences
            sentences = nltk.sent_tokenize(text)
            if not sentences:
                return text[:100] + "..."  # Return first 100 chars if no sentences found
            
            # Use the first sentence as the main idea (often contains the topic)
            main_idea = sentences[0]
            
            # If the first sentence is too short, look for a more substantial one
            if len(main_idea.split()) < 5:
                for sentence in sentences[1:]:
                    if len(sentence.split()) >= 5:
                        main_idea = sentence
                        break
            
            return main_idea
            
        except Exception as e:
            logger.error(f"Error extracting main idea: {str(e)}")
            # Fallback: return the first 100 characters
            return text[:100] + "..."

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from a paragraph."""
        try:
            # Split into sentences
            sentences = nltk.sent_tokenize(text)
            key_points = []
            
            # Look for sentences that contain key indicators
            indicators = [
                'important', 'key', 'main', 'primary', 'significant',
                'notable', 'crucial', 'essential', 'fundamental'
            ]
            
            for sentence in sentences:
                # Check if sentence contains any indicators
                if any(indicator in sentence.lower() for indicator in indicators):
                    key_points.append(sentence)
                # Also include sentences that are likely to be key points
                elif len(sentence.split()) >= 8 and not sentence.startswith(('And', 'But', 'Or', 'So')):
                    key_points.append(sentence)
            
            # If no key points found, use the first two substantial sentences
            if not key_points and len(sentences) >= 2:
                key_points = [s for s in sentences[:2] if len(s.split()) >= 5]
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []

    def _extract_cs_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract computer science concepts from a sentence."""
        concepts = []
        
        # Computer science specific terms and patterns
        cs_terms = [
            'algorithm', 'data structure', 'programming', 'software',
            'database', 'network', 'security', 'web development',
            'function', 'class', 'object', 'variable', 'method',
            'interface', 'module', 'package', 'library', 'framework'
        ]
        
        for word, tag in pos_tags:
            if word.lower() in cs_terms:
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': sentence,
                    'domain': 'computer_science'
                })
        
        return concepts

    def _extract_language_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract language learning concepts from a sentence."""
        concepts = []
        
        # Language learning specific terms
        language_terms = [
            'vocabulary', 'grammar', 'reading', 'writing',
            'pronunciation', 'speaking', 'listening', 'sentence',
            'word', 'phrase', 'tense', 'verb', 'noun', 'adjective'
        ]
        
        for word, tag in pos_tags:
            if word.lower() in language_terms:
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': sentence,
                    'domain': 'language_learning'
                })
        
        return concepts

    def _extract_math_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract mathematics concepts from a sentence."""
        concepts = []
        
        # Mathematics specific terms
        math_terms = [
            'algebra', 'calculus', 'geometry', 'statistics',
            'equation', 'function', 'theorem', 'proof',
            'number', 'formula', 'variable', 'constant',
            'derivative', 'integral', 'matrix', 'vector'
        ]
        
        for word, tag in pos_tags:
            if word.lower() in math_terms:
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': sentence,
                    'domain': 'mathematics'
                })
        
        return concepts

    def _extract_science_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract science concepts from a sentence."""
        concepts = []
        
        # Science specific terms
        science_terms = [
            'physics', 'chemistry', 'biology', 'experiment',
            'theory', 'hypothesis', 'research', 'analysis',
            'molecule', 'atom', 'cell', 'organism',
            'reaction', 'force', 'energy', 'matter'
        ]
        
        for word, tag in pos_tags:
            if word.lower() in science_terms:
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': sentence,
                    'domain': 'science'
                })
        
        return concepts

    def _extract_history_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract history concepts from a sentence."""
        concepts = []
        
        # History specific terms
        history_terms = [
            'period', 'era', 'century', 'event',
            'civilization', 'culture', 'war', 'revolution',
            'dynasty', 'empire', 'kingdom', 'republic',
            'treaty', 'battle', 'conquest', 'independence'
        ]
        
        for word, tag in pos_tags:
            if word.lower() in history_terms:
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': sentence,
                    'domain': 'history'
                })
        
        return concepts

    def _extract_business_concepts(self, sentence: str, pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract business concepts from a sentence."""
        concepts = []
        
        # Business specific terms
        business_terms = [
            'management', 'marketing', 'finance', 'economics',
            'strategy', 'organization', 'leadership', 'entrepreneurship',
            'market', 'product', 'service', 'customer',
            'investment', 'profit', 'revenue', 'business'
        ]
        
        for word, tag in pos_tags:
            if word.lower() in business_terms:
                concepts.append({
                    'term': word,
                    'type': tag,
                    'context': sentence,
                    'domain': 'business'
                })
        
        return concepts

    def _generate_basic_questions(self, content: str, count: int, chapter: Chapter) -> List[QuestionCreateSchema]:
        """Generate basic questions from content when other methods fail."""
        questions = []
        try:
            logger.info("Starting basic question generation")
            
            # Split content into sentences
            sentences = nltk.sent_tokenize(content)
            logger.info(f"Split content into {len(sentences)} sentences")
            
            # Generate questions for each sentence
            for sentence in sentences[:count]:
                if len(sentence.split()) < 5:  # Skip very short sentences
                    continue
                
                # Create a simple question
                question_text = f"What is the main point of this statement: '{sentence}'?"
                
                # Generate options
                options = [sentence]  # Correct answer
                
                # Add other sentences as options
                other_sentences = [s for s in sentences if s != sentence]
                options.extend(random.sample(other_sentences, min(3, len(other_sentences))))
                
                if len(options) >= 4:
                    try:
                        question = QuestionCreateSchema(
                            question_text=question_text,
                            question_type="multiple_choice",
                            options=options,  # Pass as list
                            correct_answer='A',  # First option is always correct
                            difficulty="medium",
                            chapter_id=chapter.id
                        )
                        questions.append(question)
                        logger.info(f"Successfully created basic question: {question_text}")
                    except Exception as e:
                        logger.error(f"Error creating question schema: {str(e)}", exc_info=True)
                        continue
            
            logger.info(f"Generated {len(questions)} basic questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating basic questions: {str(e)}", exc_info=True)
            return []