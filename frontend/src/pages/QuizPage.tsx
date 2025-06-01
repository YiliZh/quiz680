import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Box, Typography, Paper, Radio, RadioGroup, FormControlLabel, Button, Alert } from '@mui/material'
import axios from 'axios'

function QuizPage() {
  const { chapterId } = useParams()
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)

  const { data: questions } = useQuery({
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
    onSuccess: () => {
      setShowFeedback(true)
    }
  })

  const handleSubmit = (questionId: number) => {
    if (selectedAnswer !== null) {
      submitMutation.mutate({ questionId, chosenIdx: selectedAnswer })
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Quiz
      </Typography>
      {questions?.map((question: any) => (
        <Paper key={question.id} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {question.q_text}
          </Typography>
          <RadioGroup
            value={selectedAnswer}
            onChange={(e) => setSelectedAnswer(Number(e.target.value))}
          >
            {question.options.map((option: string, index: number) => (
              <FormControlLabel
                key={index}
                value={index}
                control={<Radio />}
                label={option}
              />
            ))}
          </RadioGroup>
          <Button
            variant="contained"
            onClick={() => handleSubmit(question.id)}
            disabled={selectedAnswer === null || submitMutation.isPending}
            sx={{ mt: 2 }}
          >
            Submit
          </Button>
          {showFeedback && submitMutation.data && (
            <Alert severity={submitMutation.data.is_correct ? 'success' : 'error'} sx={{ mt: 2 }}>
              {submitMutation.data.is_correct ? 'Correct!' : 'Incorrect.'}
              <br />
              {submitMutation.data.explanation}
            </Alert>
          )}
        </Paper>
      ))}
    </Box>
  )
}

export default QuizPage 