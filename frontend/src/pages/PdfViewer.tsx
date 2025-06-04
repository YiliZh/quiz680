import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Viewer, Worker } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import {
  Container,
  Box,
  Typography,
  CircularProgress,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Collapse,
  IconButton,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { api } from '../services/api';

interface Chapter {
  chapter_no: number;
  title: string;
}

interface ProcessingStatus {
  status: 'processing' | 'completed' | 'error';
  message: string;
  logs: string[];
}

const PdfViewer: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const [searchParams] = useSearchParams();
  const initialChapter = parseInt(searchParams.get('chapter') || '1');
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState(initialChapter);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>({
    status: 'processing',
    message: 'Processing PDF...',
    logs: [],
  });
  const [showLogs, setShowLogs] = useState(true);

  // Create the default layout plugin instance
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  useEffect(() => {
    if (uploadId) {
      console.log("start to load pdf")
      console.log(api.defaults.baseURL)
      const url = `${api.defaults.baseURL}/uploads/${uploadId}/pdf`;
      console.log(url)
      setPdfUrl(url);
      
      // Start polling for processing status
      const pollInterval = setInterval(async () => {
        try {
          const response = await api.get(`/uploads/${uploadId}/status`);
          const { status, message, logs } = response.data;
          
          setProcessingStatus(prev => ({
            status,
            message,
            logs: [...prev.logs, ...logs],
          }));

          if (status === 'completed' || status === 'error') {
            clearInterval(pollInterval);
            if (status === 'error') {
              setError(message);
            }
          }
        } catch (err) {
          console.error('Error fetching processing status:', err);
        }
      }, 1000); // Poll every second

      return () => clearInterval(pollInterval);
    }
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

  const handleChapterChange = (event: any) => {
    const chapterNo = event.target.value;
    setSelectedChapter(chapterNo);
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
      {/* Processing Status */}
      {processingStatus.status === 'processing' && (
        <Box mb={2}>
          <Alert 
            severity="info"
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => setShowLogs(!showLogs)}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
          >
            {processingStatus.message}
          </Alert>
          <Collapse in={showLogs}>
            <Paper 
              elevation={1} 
              sx={{ 
                mt: 1, 
                p: 2, 
                maxHeight: '200px', 
                overflow: 'auto',
                backgroundColor: '#f5f5f5'
              }}
            >
              {processingStatus.logs.map((log, index) => (
                <Typography 
                  key={index} 
                  variant="body2" 
                  component="pre" 
                  sx={{ 
                    fontFamily: 'monospace',
                    margin: '4px 0',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {log}
                </Typography>
              ))}
            </Paper>
          </Collapse>
        </Box>
      )}

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
        
        {pdfUrl && (
          <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
            <div style={{ height: '100%', width: '100%' }}>
              <Viewer
                fileUrl={pdfUrl}
                plugins={[defaultLayoutPluginInstance]}
                onDocumentLoad={() => setLoading(false)}
                httpHeaders={{
                  'Authorization': `Bearer ${localStorage.getItem('token')}`,
                }}
              />
            </div>
          </Worker>
        )}
      </Paper>
    </Container>
  );
};

export default PdfViewer;