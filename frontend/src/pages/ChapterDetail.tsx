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
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  PictureAsPdf as PdfIcon,
  Quiz as QuizIcon,
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
}

const ChapterDetail: React.FC = () => {
  const { chapterId } = useParams<{ chapterId: string }>();
  const navigate = useNavigate();
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

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
      
      console.log('Making API request to:', `/chapters/${chapterId}`);
      const response = await api.get(`/chapters/${chapterId}`);
      console.log('API response received:', response.data);
      
      setChapter(response.data);
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

  const handleGenerateQuestions = async () => {
    if (!chapter) return;
    
    try {
      setGeneratingQuestions(true);
      setGenerationError(null);
      
      // Generate questions
      await api.post(`/chapters/${chapterId}/generate-questions?num_questions=5`);
      
      // Navigate to quiz page
      navigate(`/quiz/${chapterId}`);
    } catch (err: any) {
      setGenerationError(err.response?.data?.detail || 'Failed to generate questions');
      console.error('Error generating questions:', err);
    } finally {
      setGeneratingQuestions(false);
    }
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

        <Box display="flex" gap={2}>
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
            color="primary"
            startIcon={<QuizIcon />}
            onClick={handleGenerateQuestions}
            disabled={generatingQuestions}
          >
            {generatingQuestions ? 'Generating Questions...' : 'Take Quiz'}
          </Button>
        </Box>

        {generationError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {generationError}
          </Alert>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Full Content
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {chapter.content}
        </Typography>
      </Paper>
    </Container>
  );
};

export default ChapterDetail; 