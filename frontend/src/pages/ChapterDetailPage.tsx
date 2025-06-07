import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert
} from '@mui/material'
import SmartToy from '@mui/icons-material/SmartToy'
import { api } from '../services/api'

function ChapterDetailPage() {
  const { chapterId } = useParams()
  const navigate = useNavigate()
  const [openDialog, setOpenDialog] = useState(false)
  const [content, setContent] = useState('')
  const [numQuestions, setNumQuestions] = useState(5)
  const [difficulty, setDifficulty] = useState('mixed')
  const [error, setError] = useState<string | null>(null)
  const [generatorType, setGeneratorType] = useState<'default' | 'chatgpt'>('default')

  const handleOpenDialog = (type: 'default' | 'chatgpt') => {
    setGeneratorType(type)
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setError(null)
  }

  const handleGenerateQuestions = async () => {
    try {
      const formData = new FormData()
      formData.append('content', content)
      formData.append('num_questions', numQuestions.toString())
      formData.append('difficulty', difficulty)
      formData.append('generator_type', generatorType)

      const response = await fetch(`${api.defaults.baseURL}/questions/generate`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate questions')
      }

      const data = await response.json()
      handleCloseDialog()
      // Navigate to the quiz page with the generated questions
      navigate(`/chapters/${chapterId}/quiz`)
    } catch (error) {
      console.error('Error generating questions:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate questions')
    }
  }

  return (
    <Box p={3}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Chapter Details
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            onClick={() => handleOpenDialog('default')}
          >
            Generate Questions
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => handleOpenDialog('chatgpt')}
            startIcon={<SmartToy />}
          >
            Generate via ChatGPT
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate(`/chapters/${chapterId}/quiz`)}
          >
            Take Quiz
          </Button>
        </Box>
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {generatorType === 'chatgpt' ? 'Generate Questions via ChatGPT' : 'Generate Questions'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            fullWidth
            multiline
            rows={4}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            label="Enter content"
            margin="normal"
          />
          <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <TextField
              type="number"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              label="Number of Questions"
              InputProps={{ inputProps: { min: 1, max: 10 } }}
            />
            <FormControl>
              <InputLabel>Difficulty</InputLabel>
              <Select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                label="Difficulty"
              >
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="hard">Hard</MenuItem>
                <MenuItem value="mixed">Mixed</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleGenerateQuestions}
            disabled={!content}
            color={generatorType === 'chatgpt' ? 'secondary' : 'primary'}
            startIcon={generatorType === 'chatgpt' ? <SmartToy /> : undefined}
          >
            Generate Questions
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ChapterDetailPage 