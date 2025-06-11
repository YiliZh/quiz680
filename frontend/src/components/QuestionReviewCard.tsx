import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  Box,
  Alert,
} from '@mui/material';
import { api } from '../services/api';

interface QuestionReviewCardProps {
  question: {
    id: number;
    question_text: string;
    question_type: string;
    options: string[];
    correct_answer: string;
    explanation?: string;
    chapter_title: string;
    book_title: string;
  };
  onComplete: () => void;
}

const QuestionReviewCard: React.FC<QuestionReviewCardProps> = ({ question, onComplete }) => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
    setIsCorrect(null);
  };

  const checkAnswer = () => {
    // Convert the correct answer letter to index (A=0, B=1, etc.)
    const correctIndex = question.correct_answer.charCodeAt(0) - 'A'.charCodeAt(0);
    const selectedIndex = question.options.indexOf(selectedAnswer);
    const correct = selectedIndex === correctIndex;
    setIsCorrect(correct);
  };

  const handleComplete = async () => {
    try {
      await api.post(`/exam-history/review-recommendations/${question.id}/complete`);
      onComplete();
      setShowAnswer(false);
      setSelectedAnswer('');
      setIsCorrect(null);
    } catch (error) {
      console.error('Error completing review:', error);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {question.question_text}
        </Typography>

        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {question.book_title} - {question.chapter_title}
        </Typography>

        <RadioGroup
          value={selectedAnswer}
          onChange={(e) => handleAnswerSelect(e.target.value)}
        >
          {question.options.map((option, index) => (
            <FormControlLabel
              key={index}
              value={option}
              control={<Radio />}
              label={option}
              disabled={showAnswer}
            />
          ))}
        </RadioGroup>

        {!showAnswer && (
          <Box mt={2}>
            <Button
              variant="contained"
              onClick={checkAnswer}
              disabled={!selectedAnswer}
            >
              Check Answer
            </Button>
          </Box>
        )}

        {isCorrect !== null && (
          <Box mt={2}>
            <Alert severity={isCorrect ? "success" : "error"}>
              {isCorrect ? "Correct!" : "Incorrect. The correct answer is: " + question.options[question.correct_answer.charCodeAt(0) - 'A'.charCodeAt(0)]}
            </Alert>
            {question.explanation && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {question.explanation}
              </Typography>
            )}
            <Button
              variant="contained"
              color="primary"
              onClick={handleComplete}
              sx={{ mt: 2 }}
            >
              Mark as Reviewed
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default QuestionReviewCard; 