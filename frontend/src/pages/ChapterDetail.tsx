import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Chip,
  IconButton,
  CircularProgress,
  Button,
  Alert,
  Stack,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  PictureAsPdf as PdfIcon,
  Quiz as QuizIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';
import { api } from '../services/api';

interface Chapter {
  id: number;
  chapter_no: number;
  title: string;
  content: string;
  summary: string;
  keywords: string;
  upload_id: number;
  has_questions: boolean;
  question_count?: number;
}

const ChapterDetail: React.FC = () => {
  const { chapterId } = useParams<{ chapterId: string }>();
  const navigate = useNavigate();
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generationLogs, setGenerationLogs] = useState<string[]>([]);
  const [showLogs, setShowLogs] = useState(false);
  
  // New state for question generation dialog
  const [openDialog, setOpenDialog] = useState(false);
  const [content, setContent] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('mixed');
  const [generatorType, setGeneratorType] = useState<'default' | 'chatgpt'>('default');

  useEffect(() => {
    console.log('ChapterDetail mounted with chapterId:', chapterId);
    fetchChapter();
  }, [chapterId]);

  const fetchChapter = async () => {
    if (!chapterId) {
      console.error('No chapterId provided');
      setError('Invalid chapter ID');
      setLoading(false);
      return;
    }

    console.log('Fetching chapter details for ID:', chapterId);
    try {
      setLoading(true);
      setError(null);
      
      // Fetch chapter details
      console.log('Making API request to:', `/chapters/${chapterId}`);
      const chapterResponse = await api.get(`/chapters/${chapterId}`);
      console.log('API response received:', chapterResponse.data);
      
      // Fetch question count
      const questionsResponse = await api.get(`/chapters/${chapterId}/questions`);
      const questionCount = questionsResponse.data.length;
      
      setChapter({
        ...chapterResponse.data,
        question_count: questionCount
      });
    } catch (err: any) {
      console.error('Error fetching chapter:', {
        error: err,
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        config: err.config
      });
      
      setError(err.response?.data?.detail || 'Failed to fetch chapter details');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  const handlePdfView = () => {
    if (chapter) {
      window.open(`/pdf-viewer/${chapter.upload_id}?chapter=${chapter.chapter_no}`, '_blank');
    }
  };

  const handleOpenDialog = (type: 'default' | 'chatgpt') => {
    setGeneratorType(type);
    setContent(chapter?.content || '');
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setGenerationError(null);
  };

  const handleGenerateQuestions = async () => {
    if (!chapter) return;
    
    try {
      setGeneratingQuestions(true);
      setGenerationError(null);
      setGenerationLogs([]);
      setShowLogs(true);
      
      // Add initial log
      setGenerationLogs(prev => [...prev, 'Starting question generation process...']);
      
      const formData = new FormData();
      formData.append('content', content);
      formData.append('num_questions', numQuestions.toString());
      formData.append('difficulty', difficulty);
      formData.append('generator_type', generatorType);

      const response = await fetch(`${api.defaults.baseURL}/questions/generate`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate questions');
      }

      // Add success log
      setGenerationLogs(prev => [...prev, 'Question generation completed successfully!']);
      
      // Refresh chapter data to update has_questions status
      await fetchChapter();
      handleCloseDialog();
    } catch (err: any) {
      setGenerationError(err.response?.data?.detail || 'Failed to generate questions');
      setGenerationLogs(prev => [...prev, `Error: ${err.response?.data?.detail || 'Failed to generate questions'}`]);
      console.error('Error generating questions:', err);
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleStartQuiz = () => {
    if (chapter) {
      navigate(`/quiz/${chapterId}`);
    }
  };

  const toggleLogs = () => {
    setShowLogs(!showLogs);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !chapter) {
    return (
      <Container>
        <Typography color="error" variant="h6">
          {error || 'Chapter not found'}
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={handleBack} color="primary">
          <BackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          {chapter.title}
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Summary
        </Typography>
        <Typography variant="body1" paragraph>
          {chapter.summary}
        </Typography>
        
        <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
          {chapter.keywords.split(',').map((keyword, index) => (
            <Chip
              key={index}
              label={keyword.trim()}
              size="small"
              sx={{ m: 0.5 }}
            />
          ))}
        </Box>

        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<PdfIcon />}
            onClick={handlePdfView}
          >
            View in PDF
          </Button>
          <Button
            variant="contained"
            onClick={() => handleOpenDialog('default')}
            startIcon={<QuizIcon />}
            disabled={generatingQuestions}
          >
            Generate Questions
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => handleOpenDialog('chatgpt')}
            startIcon={<SmartToyIcon />}
            disabled={generatingQuestions}
          >
            Generate via ChatGPT
          </Button>
          {chapter.has_questions && (
            <Button
              variant="outlined"
              onClick={handleStartQuiz}
              startIcon={<QuizIcon />}
            >
              Take Quiz
            </Button>
          )}
        </Stack>

        {generationError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {generationError}
          </Alert>
        )}

        {generationLogs.length > 0 && (
          <Box mt={2}>
            <Button
              onClick={toggleLogs}
              endIcon={showLogs ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {showLogs ? 'Hide Logs' : 'Show Logs'}
            </Button>
            <Collapse in={showLogs}>
              <Paper variant="outlined" sx={{ p: 2, mt: 1 }}>
                {generationLogs.map((log, index) => (
                  <Typography key={index} variant="body2">
                    {log}
                  </Typography>
                ))}
              </Paper>
            </Collapse>
          </Box>
        )}
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {generatorType === 'chatgpt' ? 'Generate Questions via ChatGPT' : 'Generate Questions'}
        </DialogTitle>
        <DialogContent>
          {generationError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {generationError}
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
            disabled={!content || generatingQuestions}
            color={generatorType === 'chatgpt' ? 'secondary' : 'primary'}
            startIcon={generatorType === 'chatgpt' ? <SmartToyIcon /> : undefined}
          >
            {generatingQuestions ? 'Generating...' : 'Generate Questions'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChapterDetail; 