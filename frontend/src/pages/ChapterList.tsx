import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Box,
  Pagination,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Book as BookIcon,
  PictureAsPdf as PdfIcon,
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
} from '@mui/icons-material';
import { api } from '../services/api';

interface Chapter {
  id: number;
  chapter_no: number;
  title: string;
  summary: string;
  keywords: string;
}

const ChapterList: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const navigate = useNavigate();
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchChapters();
  }, [uploadId, page]);

  const fetchChapters = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * itemsPerPage;
      const response = await api.get(`/uploads/${uploadId}/chapters/summary?skip=${skip}&limit=${itemsPerPage}`);
      setChapters(response.data);
      // Assuming we get total count from the API
      setTotalPages(Math.ceil(response.data.length / itemsPerPage));
    } catch (err) {
      setError('Failed to fetch chapters');
      console.error('Error fetching chapters:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChapterClick = (chapterId: number) => {
    navigate(`/chapters/${chapterId}`);
  };

  const handlePdfView = (chapterNo: number) => {
    // Open PDF viewer at specific chapter
    window.open(`/pdf-viewer/${uploadId}?chapter=${chapterNo}`, '_blank');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" variant="h6">
          {error}
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Chapter Summaries
      </Typography>

      <Grid container spacing={3}>
        {chapters.map((chapter) => (
          <Grid item xs={12} key={chapter.id}>
            <Card 
              sx={{ 
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 3,
                },
              }}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {chapter.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {chapter.summary}
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
                      {chapter.keywords.split(',').map((keyword, index) => (
                        <Chip
                          key={index}
                          label={keyword.trim()}
                          size="small"
                          sx={{ m: 0.5 }}
                        />
                      ))}
                    </Box>
                  </Box>
                  <Box display="flex" gap={1}>
                    <Tooltip title="View Chapter">
                      <IconButton 
                        onClick={() => handleChapterClick(chapter.id)}
                        color="primary"
                      >
                        <BookIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="View in PDF">
                      <IconButton 
                        onClick={() => handlePdfView(chapter.chapter_no)}
                        color="secondary"
                      >
                        <PdfIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box display="flex" justifyContent="center" mt={4}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={(_, value) => setPage(value)}
          color="primary"
          showFirstButton
          showLastButton
        />
      </Box>
    </Container>
  );
};

export default ChapterList; 