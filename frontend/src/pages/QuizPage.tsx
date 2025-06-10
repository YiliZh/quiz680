import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { 
  Box, 
  Typography, 
  Paper, 
  Radio, 
  RadioGroup, 
  FormControlLabel, 
  Button, 
  Alert,
  LinearProgress,
  Card,
  CardContent,
  Stack,
  Switch,
  FormControl,
  FormGroup
} from '@mui/material'
import { api } from '../services/api'
import { useQuestions, useSubmitAnswer } from '../api/hooks'

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  options: string[];
  correct_answer: string;
}

function QuizPage() {
  const { chapterId } = useParams()
  const navigate = useNavigate()
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({})
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)
  const [currentAnswerFeedback, setCurrentAnswerFeedback] = useState<{ is_correct: boolean; explanation?: string } | null>(null)
  const [showAnswer, setShowAnswer] = useState(true)
  const [startTime] = useState(Date.now())

  const { data: questions = [], isLoading } = useQuestions(chapterId!) as { data: Question[] | undefined, isLoading: boolean }
  const submitAnswer = useSubmitAnswer()

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }))
    // Clear feedback when selecting a new answer
    setCurrentAnswerFeedback(null)
  }

  const handleSubmit = async (questionId: number) => {
    const selectedAnswer = selectedAnswers[questionId]
    if (selectedAnswer === undefined) return

    try {
      const currentQuestion = questions[currentQuestionIndex]
      let answerToSubmit = selectedAnswer

      if (currentQuestion.question_type === "multiple_choice") {
        // Get the index of the selected answer in the options array
        const selectedIndex = currentQuestion.options.indexOf(selectedAnswer)
        if (selectedIndex === -1) {
          console.error('Selected answer not found in options')
          return
        }

        // Convert the selected answer to a letter (A, B, C, D)
        answerToSubmit = String.fromCharCode(65 + selectedIndex)
      } else if (currentQuestion.question_type === "true_false") {
        // For true/false questions, convert A/B to True/False
        answerToSubmit = selectedAnswer === "A" ? "True" : "False"
      }

      const result = await submitAnswer.mutateAsync({
        question_id: questionId,
        chosen_answer: answerToSubmit
      })
      
      setCurrentAnswerFeedback({
        is_correct: result.is_correct,
        explanation: result.is_correct ? "Correct!" : "Incorrect. Try again!"
      })

      if (result.is_correct) {
        setScore(prev => prev + 1)
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
    }
  }

  const handleNext = async () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
      setCurrentAnswerFeedback(null)
    } else {
      // Create exam session when quiz is completed
      try {
        const examSession = await api.post('/exam-history/sessions', {
          chapter_id: chapterId,
          score: score,
          total_questions: questions.length,
          duration: Math.floor((Date.now() - startTime) / 1000) // Convert to seconds
        })
        
        // Create review recommendations for failed questions
        const failedQuestions = questions.filter((q, index) => {
          const attempt = selectedAnswers[q.id]
          return !attempt || attempt !== q.correct_answer
        })
        
        if (failedQuestions.length > 0) {
          await api.post('/exam-history/review-recommendations', {
            exam_session_id: examSession.data.id,
            question_ids: failedQuestions.map(q => q.id)
          })
        }
        
        setShowResults(true)
      } catch (error) {
        console.error('Error saving exam session:', error)
        setShowResults(true) // Still show results even if saving fails
      }
    }
  }

  if (isLoading) {
    return <LinearProgress />
  }

  if (!questions || questions.length === 0) {
    return (
      <Box p={3}>
        <Alert severity="info">No questions available for this chapter.</Alert>
      </Box>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]

  return (
    <Box sx={{ p: 3 }}>
      {showResults ? (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Quiz Complete!
          </Typography>
          <Typography>
            Your score: {score} out of {questions.length}
          </Typography>
          <Button
            variant="contained"
            onClick={() => navigate(`/chapters/${chapterId}`)}
            sx={{ mt: 2 }}
          >
            Back to Chapter
          </Button>
        </Paper>
      ) : (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Question {currentQuestionIndex + 1} of {questions.length}
          </Typography>
          
          <Typography variant="body1" paragraph>
            {currentQuestion.question_text}
          </Typography>

          <RadioGroup
            value={selectedAnswers[currentQuestion.id] || ''}
            onChange={(e) => handleAnswerSelect(currentQuestion.id, e.target.value)}
          >
            {currentQuestion.options.map((option: string, index: number) => (
              <FormControlLabel
                key={index}
                value={option}
                control={<Radio />}
                label={option}
              />
            ))}
          </RadioGroup>

          {currentAnswerFeedback && (
            <Alert 
              severity={currentAnswerFeedback.is_correct ? "success" : "error"}
              sx={{ mt: 2 }}
            >
              {currentAnswerFeedback.explanation}
            </Alert>
          )}

          <Box display="flex" justifyContent="space-between" alignItems="center" mt={3}>
            <FormControl component="fieldset">
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={showAnswer}
                      onChange={(e) => setShowAnswer(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Show Answer"
                />
              </FormGroup>
            </FormControl>

            <Box>
              <Button
                variant="outlined"
                onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
                disabled={currentQuestionIndex === 0}
                sx={{ mr: 1 }}
              >
                Previous
              </Button>
              {currentAnswerFeedback ? (
                <Button
                  variant="contained"
                  onClick={handleNext}
                >
                  {currentQuestionIndex === questions.length - 1 ? 'Finish' : 'Next'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={() => handleSubmit(currentQuestion.id)}
                  disabled={!selectedAnswers[currentQuestion.id] || submitAnswer.isPending}
                >
                  Submit Answer
                </Button>
              )}
            </Box>
          </Box>
        </Paper>
      )}
    </Box>
  )
}

export default QuizPage 