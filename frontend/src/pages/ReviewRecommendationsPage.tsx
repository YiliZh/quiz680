import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import QuestionReviewCard from '../components/QuestionReviewCard';

interface ReviewRecommendation {
  id: number;
  question_text: string;
  question_type: string;
  options: string[];
  correct_answer: string;
  explanation?: string;
  chapter_title: string;
  book_title: string;
  last_reviewed_at: string | null;
  next_review_at: string;
  review_stage: number;
  days_until_review: number;
}

function ReviewRecommendationsPage() {
  const [selectedRecommendation, setSelectedRecommendation] = useState<ReviewRecommendation | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['review-recommendations'],
    queryFn: async () => {
      const response = await api.get('/exam-history/review-recommendations');
      return response.data;
    }
  });

  const completeReview = useMutation({
    mutationFn: async (recommendationId: number) => {
      await api.post(`/exam-history/review-recommendations/${recommendationId}/complete`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review-recommendations'] });
      setOpenDialog(false);
      setSelectedRecommendation(null);
    }
  });

  const handleReview = async (recommendation: ReviewRecommendation) => {
    try {
      const response = await api.get(`/exam-history/review-recommendations/${recommendation.id}/question`);
      setSelectedRecommendation({ ...recommendation, ...response.data });
      setOpenDialog(true);
    } catch (error) {
      console.error('Error fetching question details:', error);
    }
  };

  const handleComplete = () => {
    if (selectedRecommendation) {
      completeReview.mutate(selectedRecommendation.id);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading review recommendations
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom>
        Review Recommendations
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Question</TableCell>
              <TableCell>Chapter</TableCell>
              <TableCell>Book</TableCell>
              <TableCell>Next Review</TableCell>
              <TableCell>Review Stage</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.items.map((recommendation: ReviewRecommendation) => (
              <TableRow key={recommendation.id}>
                <TableCell>{recommendation.question_text}</TableCell>
                <TableCell>{recommendation.chapter_title}</TableCell>
                <TableCell>{recommendation.book_title}</TableCell>
                <TableCell>
                  {new Date(recommendation.next_review_at).toLocaleDateString()}
                  {recommendation.days_until_review > 0 && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      ({recommendation.days_until_review} days left)
                    </Typography>
                  )}
                </TableCell>
                <TableCell>{recommendation.review_stage}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => handleReview(recommendation)}
                  >
                    Review
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Review Question</DialogTitle>
        <DialogContent>
          {selectedRecommendation && (
            <QuestionReviewCard
              question={selectedRecommendation}
              onComplete={handleComplete}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default ReviewRecommendationsPage; 