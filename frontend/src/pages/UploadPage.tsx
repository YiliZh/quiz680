import React, { useState, useEffect } from 'react'
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  Alert, 
  CircularProgress, 
  Collapse, 
  IconButton 
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useUploadFile } from '../api/hooks'
import { api } from '../services/api'
import type { Upload } from '../types/index'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import VisibilityIcon from '@mui/icons-material/Visibility'
import { format } from 'date-fns'

// Type guard to check if an object has processing_logs
function hasProcessingLogs(obj: any): obj is Upload & { processing_logs: string } {
  return obj && typeof obj.processing_logs === 'string'
}

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedUploads, setExpandedUploads] = useState<Set<number>>(new Set())
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  console.log('UploadPage: Component rendered, user:', user?.id)

  useEffect(() => {
    if (!user) {
      console.log('UploadPage: No user found, redirecting to login')
      navigate('/auth')
    }
  }, [user, navigate])

  const { data: uploads, isLoading: isLoadingUploads, error: uploadsError } = useQuery<Upload[], Error>({
    queryKey: ['uploads'],
    queryFn: async () => {
      const response = await api.get('/uploads')
      return response.data
    },
    enabled: !!user,
    retry: false,
    refetchInterval: (query) => {
      // If any upload is in processing state, refetch every 2 seconds
      const queryData = query.state.data as Upload[] | undefined
      return queryData?.some((upload) => upload.status === 'processing') ? 2000 : false
    }
  })

  const uploadMutation = useUploadFile()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      console.log('UploadPage: File selected:', {
        name: file.name,
        size: file.size,
        type: file.type
      })
      if (file.type !== 'application/pdf') {
        console.error('UploadPage: Invalid file type:', file.type)
        setError('Please select a PDF file')
        return
      }
      setSelectedFile(file)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      console.error('UploadPage: No file selected')
      setError('Please select a file first')
      return
    }

    console.log('UploadPage: Starting file upload:', {
      fileName: selectedFile.name,
      fileSize: selectedFile.size,
      fileType: selectedFile.type
    })

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      console.log('UploadPage: Sending upload request')
      const result = await uploadMutation.mutateAsync(formData)
      console.log('UploadPage: Upload successful:', result)
      setSelectedFile(null)
      setError(null)
      queryClient.invalidateQueries({ queryKey: ['uploads'] })
    } catch (error: any) {
      console.error('UploadPage: Upload failed:', {
        error: error,
        response: error.response?.data,
        status: error.response?.status
      })
      setError(error.response?.data?.detail || 'Error uploading file')
    }
  }

  const toggleUploadExpansion = (uploadId: number) => {
    setExpandedUploads(prev => {
      const newSet = new Set(prev)
      if (newSet.has(uploadId)) {
        newSet.delete(uploadId)
      } else {
        newSet.add(uploadId)
      }
      return newSet
    })
  }

  if (!user) {
    return null
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Upload PDF
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <input
          accept=".pdf"
          style={{ display: 'none' }}
          id="file-input"
          type="file"
          onChange={handleFileSelect}
        />
        <label htmlFor="file-input">
          <Button
            variant="contained"
            component="span"
            disabled={uploadMutation.isPending}
          >
            Select PDF
          </Button>
        </label>
        {selectedFile && (
          <Typography sx={{ mt: 1 }}>
            Selected file: {selectedFile.name}
          </Typography>
        )}
      </Box>

      <Button
        variant="contained"
        color="primary"
        onClick={handleUpload}
        disabled={!selectedFile || uploadMutation.isPending}
        sx={{ mr: 2 }}
      >
        {uploadMutation.isPending ? (
          <>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            Uploading...
          </>
        ) : (
          'Upload'
        )}
      </Button>

      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
        Your Uploads
      </Typography>

      {isLoadingUploads ? (
        <CircularProgress />
      ) : uploadsError ? (
        <Alert severity="error">
          Error loading uploads: {uploadsError.message}
        </Alert>
      ) : uploads && Array.isArray(uploads) && uploads.length > 0 ? (
        <Box>
          {uploads.map((upload: Upload) => (
            <Paper key={upload.id} sx={{ mb: 2, p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="h6">{upload.title}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Uploaded: {format(new Date(upload.created_at), 'MMM d, yyyy HH:mm')}
                  </Typography>
                  <Typography>Status: {upload.status}</Typography>
                  {upload.description && (
                    <Typography>Description: {upload.description}</Typography>
                  )}
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <IconButton 
                    onClick={() => navigate(`/uploads/${upload.id}/chapters`)}
                    color="primary"
                    title="View Details"
                  >
                    <VisibilityIcon />
                  </IconButton>
                  {upload.status === 'processing' && (
                    <IconButton onClick={() => toggleUploadExpansion(upload.id)}>
                      {expandedUploads.has(upload.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  )}
                </Box>
              </Box>
              <Collapse in={expandedUploads.has(upload.id)}>
                {upload.processing_logs !== null && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Processing Logs:
                    </Typography>
                    <Box
                      component="pre"
                      sx={{
                        maxHeight: '200px',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                        m: 0,
                        p: 1,
                        bgcolor: 'grey.50',
                        borderRadius: 1
                      }}
                    >
                      {upload.processing_logs}
                    </Box>
                  </Box>
                )}
              </Collapse>
            </Paper>
          ))}
        </Box>
      ) : (
        <Typography>No uploads yet</Typography>
      )}
    </Box>
  )
} 