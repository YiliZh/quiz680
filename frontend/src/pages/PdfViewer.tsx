import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Document, Page, pdfjs } from 'react-pdf';
import {
  Container,
  Box,
  IconButton,
  Typography,
  CircularProgress,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
} from '@mui/icons-material';
import { api } from '../services/api';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface Chapter {
  chapter_no: number;
  title: string;
}

const PdfViewer: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const [searchParams] = useSearchParams();
  const initialChapter = parseInt(searchParams.get('chapter') || '1');
  
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState(initialChapter);

  useEffect(() => {
    fetchChapters();
  }, [uploadId]);

  const fetchChapters = async () => {
    try {
      const response = await api.get(`/uploads/${uploadId}/chapters/summary`);
      setChapters(response.data);
    } catch (err) {
      setError('Failed to fetch chapters');
      console.error('Error fetching chapters:', err);
    }
  };

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setLoading(false);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error);
    setError('Failed to load PDF');
    setLoading(false);
  };

  const handlePrevPage = () => {
    setPageNumber((prev) => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setPageNumber((prev) => Math.min(prev + 1, numPages || prev));
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 2.0));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  const handleChapterChange = (event: any) => {
    const chapterNo = event.target.value;
    setSelectedChapter(chapterNo);
    // You might want to implement logic to jump to the correct page for this chapter
  };

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
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Chapter</InputLabel>
            <Select
              value={selectedChapter}
              onChange={handleChapterChange}
              label="Chapter"
            >
              {chapters.map((chapter) => (
                <MenuItem key={chapter.chapter_no} value={chapter.chapter_no}>
                  {chapter.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography>
            Page {pageNumber} of {numPages || '--'}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <IconButton onClick={handleZoomOut} disabled={scale <= 0.5}>
            <ZoomOutIcon />
          </IconButton>
          <IconButton onClick={handleZoomIn} disabled={scale >= 2.0}>
            <ZoomInIcon />
          </IconButton>
        </Box>
      </Box>

      <Paper 
        elevation={3} 
        sx={{ 
          p: 2, 
          display: 'flex', 
          justifyContent: 'center',
          minHeight: '80vh',
          position: 'relative'
        }}
      >
        {loading && (
          <Box 
            position="absolute" 
            top="50%" 
            left="50%" 
            sx={{ transform: 'translate(-50%, -50%)' }}
          >
            <CircularProgress />
          </Box>
        )}
        
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton 
            onClick={handlePrevPage} 
            disabled={pageNumber <= 1}
            size="large"
          >
            <PrevIcon />
          </IconButton>
          
          <Document
            file={`/api/uploads/${uploadId}/pdf`}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={null}
            options={{
              cMapUrl: 'https://unpkg.com/pdfjs-dist@3.4.120/cmaps/',
              cMapPacked: true,
            }}
          >
            <Page 
              pageNumber={pageNumber} 
              scale={scale}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
          </Document>
          
          <IconButton 
            onClick={handleNextPage} 
            disabled={pageNumber >= (numPages || 1)}
            size="large"
          >
            <NextIcon />
          </IconButton>
        </Box>
      </Paper>
    </Container>
  );
};

export default PdfViewer; 