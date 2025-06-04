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
    if (uploadId) {
      console.log('Effect triggered - uploadId:', uploadId, 'page:', page);
      fetchChapters();
    }
  }, [uploadId, page]);

  const fetchChapters = async () => {
    if (!uploadId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const skip = (page - 1) * itemsPerPage;
      console.log('Fetching chapters:', {
        page,
        skip,
        limit: itemsPerPage,
        uploadId
      });
      
      const response = await api.get(`/uploads/${uploadId}/chapters/summary?skip=${skip}&limit=${itemsPerPage}`);
      
      // Get total count from response headers
      const totalCountHeader = response.headers['x-total-count'];
      console.log('Total count header:', totalCountHeader);
      
      const totalCount = totalCountHeader ? parseInt(totalCountHeader, 10) : 0;
      const calculatedTotalPages = Math.max(1, Math.ceil(totalCount / itemsPerPage));
      
      console.log('Response details:', {
        totalCountHeader,
        totalCount,
        calculatedTotalPages,
        currentPage: page,
        chaptersReceived: response.data.length,
        headers: response.headers
      });
      
      setTotalPages(calculatedTotalPages);
      setChapters(response.data);
      
      // If current page is greater than total pages, reset to page 1
      if (page > calculatedTotalPages) {
        console.log('Resetting to page 1 because current page exceeds total pages');
        setPage(1);
      }
    } catch (err) {
      console.error('Error fetching chapters:', err);
      setError('Failed to fetch chapters. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChapterClick = (chapterId: number) => {
    navigate(`/chapters/${chapterId}`);
  };

  const handlePdfView = (chapterNo: number) => {
    window.open(`/pdf-viewer/${uploadId}?chapter=${chapterNo}`, '_blank');
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    console.log('Page change requested:', {
      from: page,
      to: value,
      totalPages
    });
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
        <Typography color="error" variant="h6" gutterBottom>
          {error}
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => fetchChapters()}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Container>
    );
  }

  console.log('Render state:', {
    chaptersCount: chapters.length,
    totalPages,
    currentPage: page,
    shouldShowPagination: totalPages > 1
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Chapter Summaries
      </Typography>

      {chapters.length === 0 ? (
        <Typography variant="body1" color="text.secondary" align="center">
          No chapters found
        </Typography>
      ) : (
        <>
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

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                showFirstButton
                showLastButton
                size="large"
                siblingCount={1}
                boundaryCount={1}
              />
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default ChapterList; 