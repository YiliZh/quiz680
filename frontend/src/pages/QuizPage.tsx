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
import axios from 'axios'

function QuizPage() {
  const { chapterId } = useParams()
  const navigate = useNavigate()
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({})
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)

  const { data: questions, isLoading } = useQuery({
    queryKey: ['questions', chapterId],
    queryFn: async () => {
      const response = await axios.get(`/api/questions/${chapterId}/questions`)
      return response.data
    }
  })

  const submitMutation = useMutation({
    mutationFn: async ({ questionId, chosenIdx }: { questionId: number; chosenIdx: number }) => {
      const response = await axios.post(`/api/questions/${questionId}/answer`, { chosen_idx: chosenIdx })
      return response.data
    },
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
  })

  const handleAnswerSelect = (questionId: number, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }))
  }

  const handleSubmit = (questionId: number) => {
    const selectedAnswer = selectedAnswers[questionId]
    if (selectedAnswer !== undefined) {
      submitMutation.mutate({ questionId, chosenIdx: selectedAnswer })
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
              Your Score: {score} out of {questions.length}
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
        <Typography variant="h5" gutterBottom>
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
          <Typography variant="h6" gutterBottom>
            {currentQuestion.q_text}
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
              disabled={selectedAnswers[currentQuestion.id] === undefined || submitMutation.isPending}
            >
              {currentQuestionIndex === questions.length - 1 ? 'Finish' : 'Next'}
            </Button>
          </Box>

          {submitMutation.data && (
            <Alert 
              severity={submitMutation.data.is_correct ? 'success' : 'error'} 
              sx={{ mt: 2 }}
            >
              {submitMutation.data.is_correct ? 'Correct!' : 'Incorrect.'}
              <br />
              {submitMutation.data.explanation}
            </Alert>
          )}
        </Paper>
      )}
    </Box>
  )
}

export default QuizPage 