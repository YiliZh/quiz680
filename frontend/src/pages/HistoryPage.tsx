import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Box,
  CircularProgress,
} from '@mui/material';
import { Book as BookIcon, Quiz as QuizIcon } from '@mui/icons-material';
import { apiService } from '../services/api';
import type { Upload } from '../services/api';

function HistoryPage() {
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUploads();
  }, []);

  const fetchUploads = async () => {
    try {
      setLoading(true);
      const data = await apiService.getUploads();
      setUploads(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching uploads:', err);
      setError('Failed to load upload history');
    } finally {
      setLoading(false);
    }
  };

  const handleViewChapters = (uploadId: number) => {
    navigate(`/uploads/${uploadId}/chapters`);
  };

  const handleStartQuiz = (chapterId: number) => {
    navigate(`/quiz/${chapterId}`);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Upload History
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Filename</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Upload Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {uploads.map((upload) => (
              <TableRow key={upload.id}>
                <TableCell>{upload.filename}</TableCell>
                <TableCell>{upload.status}</TableCell>
                <TableCell>
                  {new Date(upload.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <IconButton
                    color="primary"
                    onClick={() => handleViewChapters(upload.id)}
                    title="View Chapters"
                  >
                    <BookIcon />
                  </IconButton>
                  {upload.chapters && upload.chapters.length > 0 && (
                    <IconButton
                      color="secondary"
                      onClick={() => handleStartQuiz(upload.chapters![0].id)}
                      title="Start Quiz"
                    >
                      <QuizIcon />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default HistoryPage; 