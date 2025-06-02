import React, { useState, useEffect } from 'react'
import { Box, Button, Typography, Paper, List, ListItem, ListItemText, Alert, CircularProgress } from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useUploads, useUploadFile } from '../api/hooks'
import { Upload } from '../types'

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  console.log('UploadPage: Component rendered, user:', user?.id)

  const { data: uploads, isLoading: isLoadingUploads, error: uploadsError } = useQuery<Upload[], Error>({
    queryKey: ['uploads'],
    queryFn: useUploads,
    enabled: !!user,
    retry: false
  })

  useEffect(() => {
    if (uploadsError?.message.includes('401')) {
      console.log('UploadPage: Unauthorized access, redirecting to auth')
      navigate('/auth')
    }
  }, [uploadsError, navigate])

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

  if (!user) {
    console.log('UploadPage: No user found, redirecting to login')
    navigate('/auth')
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
            <Box key={upload.id} sx={{ mb: 2, p: 2, border: '1px solid #ddd' }}>
              <Typography variant="h6">{upload.title}</Typography>
              <Typography>Status: {upload.status}</Typography>
              {upload.description && (
                <Typography>Description: {upload.description}</Typography>
              )}
            </Box>
          ))}
        </Box>
      ) : (
        <Typography>No uploads yet</Typography>
      )}
    </Box>
  )
} 