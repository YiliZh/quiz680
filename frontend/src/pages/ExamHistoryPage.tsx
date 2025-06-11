import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  CircularProgress,
  Alert,
  TablePagination,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

interface ExamSession {
  id: number;
  chapter_title: string;
  book_title: string;
  score: number;
  total_questions: number;
  performance_percentage: number;
  completed_at: string;
  duration: number;
}

interface ReviewRecommendation {
  id: number;
  question_text: string;
  chapter_title: string;
  book_title: string;
  last_reviewed_at: string | null;
  next_review_at: string;
  review_stage: number;
  days_until_review: number;
}

function ExamHistoryPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [examSessions, setExamSessions] = useState<ExamSession[]>([]);
  const [reviewRecommendations, setReviewRecommendations] = useState<ReviewRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, [activeTab, page, rowsPerPage]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (activeTab === 0) {
        const response = await api.get('/exam-history/history', {
          params: {
            skip: page * rowsPerPage,
            limit: rowsPerPage
          }
        });
        setExamSessions(response.data.items);
        setTotalCount(response.data.total);
      } else {
        const response = await api.get('/exam-history/review-recommendations', {
          params: {
            skip: page * rowsPerPage,
            limit: rowsPerPage
          }
        });
        setReviewRecommendations(response.data.items);
        setTotalCount(response.data.total);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleCompleteReview = async (recommendationId: number) => {
    try {
      await api.post(`/exam-history/review-recommendations/${recommendationId}/complete`);
      fetchData(); // Refresh the data
    } catch (err) {
      console.error('Error completing review:', err);
      setError('Failed to complete review');
    }
  };

  const handleSkipReview = async (recommendationId: number) => {
    try {
      await api.post(`/exam-history/review-recommendations/${recommendationId}/skip`);
      fetchData(); // Refresh the data
    } catch (err) {
      console.error('Error skipping review:', err);
      setError('Failed to skip review');
    }
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

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Exam History & Reviews
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Exam History" />
          <Tab label="Review Recommendations" />
        </Tabs>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {activeTab === 0 ? (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Book</TableCell>
                  <TableCell>Chapter</TableCell>
                  <TableCell>Score</TableCell>
                  <TableCell>Performance</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {examSessions.map((session) => (
                  <TableRow key={session.id}>
                    <TableCell>{session.book_title}</TableCell>
                    <TableCell>{session.chapter_title}</TableCell>
                    <TableCell>{session.score}/{session.total_questions}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${session.performance_percentage.toFixed(1)}%`}
                        color={session.performance_percentage >= 70 ? 'success' : 'warning'}
                      />
                    </TableCell>
                    <TableCell>{formatDuration(session.duration)}</TableCell>
                    <TableCell>
                      {new Date(session.completed_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => navigate(`/exam-history/${session.id}`)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={totalCount}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      ) : (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Question</TableCell>
                  <TableCell>Book</TableCell>
                  <TableCell>Chapter</TableCell>
                  <TableCell>Review Stage</TableCell>
                  <TableCell>Next Review</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reviewRecommendations.map((rec) => (
                  <TableRow key={rec.id}>
                    <TableCell>{rec.question_text}</TableCell>
                    <TableCell>{rec.book_title}</TableCell>
                    <TableCell>{rec.chapter_title}</TableCell>
                    <TableCell>
                      <Chip
                        label={`Stage ${rec.review_stage}`}
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      {rec.days_until_review <= 0 ? (
                        <Chip label="Due Now" color="error" />
                      ) : (
                        `In ${rec.days_until_review} days`
                      )}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleCompleteReview(rec.id)}
                          disabled={rec.days_until_review > 0}
                        >
                          Complete Review
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleSkipReview(rec.id)}
                          color="secondary"
                        >
                          No Need to Review
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={totalCount}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      )}
    </Container>
  );
}

export default ExamHistoryPage; 