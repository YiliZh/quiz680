import os
from openai import AsyncOpenAI
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ChatGPTQuestionGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"

    async def generate_questions(
        self,
        content: str,
        num_questions: int = 5,
        difficulty: str = "mixed"
    ) -> List[Dict[str, Any]]:
        """
        Generate questions using ChatGPT-4.
        """
        try:
            prompt = self._create_prompt(content, num_questions, difficulty)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Create high-quality multiple choice questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Parse the response and format questions
            questions = self._parse_response(response.choices[0].message.content)
            return questions

        except Exception as e:
            logger.error(f"Error generating questions with ChatGPT: {str(e)}")
            raise

    def _create_prompt(self, content: str, num_questions: int, difficulty: str) -> str:
        """
        Create a prompt for ChatGPT to generate questions.
        """
        return f"""
        Create {num_questions} multiple choice questions based on the following content.
        Difficulty level: {difficulty}
        
        For each question:
        1. Create a clear and concise question
        2. Provide 4 options (A, B, C, D)
        3. Mark the correct answer
        4. Include an explanation for the correct answer
        
        Format each question as follows:
        Q: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct: [Letter of correct answer]
        Explanation: [Brief explanation]
        
        Content:
        {content}
        """

    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse ChatGPT's response into structured question format.
        """
        questions = []
        current_question = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Q:'):
                if current_question:
                    questions.append(current_question)
                current_question = {
                    'question_text': line[2:].strip(),
                    'options': [],
                    'question_type': 'multiple_choice'
                }
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option = line[2:].strip()
                current_question['options'].append(option)
            elif line.startswith('Correct:'):
                correct_letter = line[8:].strip()
                current_question['correct_answer'] = correct_letter
            elif line.startswith('Explanation:'):
                current_question['explanation'] = line[12:].strip()
        
        if current_question:
            questions.append(current_question)
            
        return questions 