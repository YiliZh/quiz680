import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { ArrowBack as BackIcon } from '@mui/icons-material';
import { api } from '../services/api';

interface QuestionAttempt {
  question_text: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string;
}

interface ExamSession {
  id: number;
  chapter_title: string;
  book_title: string;
  score: number;
  total_questions: number;
  performance_percentage: number;
  completed_at: string;
  duration: number;
  attempts: QuestionAttempt[];
}

function ExamSessionDetail() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState<ExamSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSessionDetails();
  }, [sessionId]);

  const fetchSessionDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/exam-history/history/${sessionId}`);
      console.log('Session details:', response.data);
      setSession(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching session details:', err);
      setError('Failed to load session details');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/exam-history');
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !session) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error || 'Session not found'}
        </Alert>
        <Button
          variant="contained"
          startIcon={<BackIcon />}
          onClick={handleBack}
          sx={{ mt: 2 }}
        >
          Back to History
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Button
          variant="outlined"
          startIcon={<BackIcon />}
          onClick={handleBack}
        >
          Back to History
        </Button>
        <Typography variant="h4" component="h1">
          Exam Session Details
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Session Overview
        </Typography>
        <Box display="flex" gap={4} mb={3}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Book
            </Typography>
            <Typography variant="body1">{session.book_title}</Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Chapter
            </Typography>
            <Typography variant="body1">{session.chapter_title}</Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Score
            </Typography>
            <Typography variant="body1">
              {session.score}/{session.total_questions}
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Performance
            </Typography>
            <Chip
              label={`${session.performance_percentage.toFixed(1)}%`}
              color={session.performance_percentage >= 70 ? 'success' : 'warning'}
            />
          </Box>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Duration
            </Typography>
            <Typography variant="body1">{formatDuration(session.duration)}</Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Completed At
            </Typography>
            <Typography variant="body1">
              {new Date(session.completed_at).toLocaleString()}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Question Attempts
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Question</TableCell>
                <TableCell>Your Answer</TableCell>
                <TableCell>Correct Answer</TableCell>
                <TableCell>Result</TableCell>
                <TableCell>Explanation</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {session.attempts.map((attempt, index) => (
                <TableRow key={index}>
                  <TableCell>{attempt.question_text}</TableCell>
                  <TableCell>{attempt.user_answer}</TableCell>
                  <TableCell>{attempt.correct_answer}</TableCell>
                  <TableCell>
                    <Chip
                      label={attempt.is_correct ? 'Correct' : 'Incorrect'}
                      color={attempt.is_correct ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell>{attempt.explanation}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}

export default ExamSessionDetail; 