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
  Stack
} from '@mui/material'
import { api } from '../services/api'
import { useQuestions, useSubmitAnswer } from '../api/hooks'

function QuizPage() {
  const { chapterId } = useParams()
  const navigate = useNavigate()
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({})
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)

  const { data: questions, isLoading } = useQuestions(chapterId!)
  const submitAnswer = useSubmitAnswer()

  const handleAnswerSelect = (questionId: number, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }))
  }

  const handleSubmit = (questionId: number) => {
    const selectedAnswer = selectedAnswers[questionId]
    if (selectedAnswer !== undefined && currentQuestion) {
      submitAnswer.mutate(
        { 
          question_id: questionId,
          chosen_answer: currentQuestion.options[selectedAnswer]
        },
        {
          onSuccess: (data) => {
            if (data.is_correct) {
              setScore(prev => prev + 1)
            }
            if (currentQuestionIndex < questions.length - 1) {
              setCurrentQuestionIndex(prev => prev + 1)
            } else {
              setShowResults(true)
            }
          }
        }
      )
    }
  }

  const handleFinish = () => {
    navigate(`/chapters/${chapterId}`)
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <LinearProgress />
      </Box>
    )
  }

  if (showResults) {
    return (
      <Box maxWidth="600px" mx="auto" mt={4}>
        <Card>
          <CardContent>
            <Typography variant="h4" gutterBottom align="center">
              Quiz Complete!
            </Typography>
            <Typography variant="h5" gutterBottom align="center">
              Your Score: {score} out of {questions?.length}
            </Typography>
            <Box display="flex" justifyContent="center" mt={3}>
              <Button variant="contained" onClick={handleFinish}>
                Return to Chapter
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    )
  }

  const currentQuestion = questions?.[currentQuestionIndex]

  return (
    <Box maxWidth="800px" mx="auto" mt={4}>
      <Box mb={3}>
        <Typography variant="h6" gutterBottom align="center" color="text.secondary">
          Question {currentQuestionIndex + 1} of {questions?.length}
        </Typography>
        <LinearProgress 
          variant="determinate" 
          value={((currentQuestionIndex + 1) / questions?.length) * 100} 
          sx={{ mb: 2 }}
        />
      </Box>

      {currentQuestion && (
        <Paper elevation={3} sx={{ p: 3 }}>
          {(() => {
            if (!currentQuestion.question_text) {
              return (
                <Typography variant="h5" gutterBottom color="primary">
                  Question {currentQuestionIndex + 1}
                </Typography>
              );
            }

            const parts = currentQuestion.question_text.split('\n\nContext:');
            const question = parts[0] || '';
            const context = parts[1] || '';
            
            return (
              <>
                <Typography variant="h5" gutterBottom color="primary" sx={{ mb: 2 }}>
                  {question}
                </Typography>
                {context && (
                  <Paper 
                    elevation={0}
                    sx={{ 
                      mb: 3, 
                      p: 2, 
                      bgcolor: 'grey.50', 
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider'
                    }}
                  >
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        fontStyle: 'italic',
                        color: 'text.secondary'
                      }}
                    >
                      {context}
                    </Typography>
                  </Paper>
                )}
              </>
            );
          })()}
          
          <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 2 }}>
            Select the correct answer:
          </Typography>
          
          <RadioGroup
            value={selectedAnswers[currentQuestion.id] ?? ''}
            onChange={(e) => handleAnswerSelect(currentQuestion.id, Number(e.target.value))}
          >
            <Stack spacing={2}>
              {currentQuestion.options.map((option: string, index: number) => (
                <FormControlLabel
                  key={index}
                  value={index}
                  control={<Radio />}
                  label={option}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    p: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                />
              ))}
            </Stack>
          </RadioGroup>

          <Box display="flex" justifyContent="space-between" mt={3}>
            <Button
              variant="outlined"
              onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
              disabled={currentQuestionIndex === 0}
            >
              Previous
            </Button>
            <Button
              variant="contained"
              onClick={() => handleSubmit(currentQuestion.id)}
              disabled={selectedAnswers[currentQuestion.id] === undefined || submitAnswer.isPending}
            >
              {currentQuestionIndex === questions.length - 1 ? 'Finish' : 'Next'}
            </Button>
          </Box>

          {submitAnswer.data && (
            <Alert 
              severity={submitAnswer.data.is_correct ? 'success' : 'error'} 
              sx={{ mt: 2 }}
            >
              {submitAnswer.data.is_correct ? 'Correct!' : 'Incorrect.'}
              <br />
              {submitAnswer.data.explanation}
            </Alert>
          )}
        </Paper>
      )}
    </Box>
  )
}

export default QuizPage 