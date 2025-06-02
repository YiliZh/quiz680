import { useState } from 'react'
import { Box, Button, Typography, Paper, List, ListItem, ListItemText, Alert } from '@mui/material'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../contexts/AuthContext'

function UploadPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string>('')

  const { data: uploads, refetch, error: queryError } = useQuery({
    queryKey: ['uploads'],
    queryFn: async () => {
      console.log('Fetching uploads...')
      try {
        const response = await api.get('/uploads')
        console.log('Uploads fetched successfully:', response.data)
        return response.data
      } catch (error: any) {
        console.error('Error fetching uploads:', error.response?.data || error.message)
        if (error.response?.status === 401 && !user) {
          console.log('Unauthorized and no user, redirecting to auth page')
          navigate('/auth')
        }
        throw error
      }
    },
    enabled: !!user // Only fetch uploads if user is authenticated
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      console.log('Starting file upload:', { filename: file.name, size: file.size, type: file.type })
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        console.log('Sending upload request to server...')
        const response = await api.post('/uploads', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        console.log('Upload successful:', response.data)
        return response.data
      } catch (error: any) {
        console.error('Upload error details:', {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message
        })
        throw error
      }
    },
    onSuccess: (data) => {
      console.log('Upload mutation succeeded:', data)
      refetch()
      setFile(null)
      setError('')
    },
    onError: (error: any) => {
      console.error('Upload mutation error:', error)
      if (error.response?.status === 401 && !user) {
        console.log('Unauthorized during upload and no user, redirecting to auth page')
        navigate('/auth')
      } else {
        const errorMessage = error.response?.data?.detail || 'Failed to upload file'
        console.error('Upload error message:', errorMessage)
        setError(errorMessage)
      }
    }
  })

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0]
      console.log('File selected:', { 
        name: selectedFile.name, 
        size: selectedFile.size, 
        type: selectedFile.type 
      })
      setFile(selectedFile)
      setError('')
    }
  }

  const handleUpload = () => {
    if (file) {
      console.log('Initiating file upload...')
      uploadMutation.mutate(file)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload PDF
      </Typography>
      <Paper sx={{ p: 2, mb: 4 }}>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          id="file-input"
        />
        <label htmlFor="file-input">
          <Button variant="contained" component="span">
            Select File
          </Button>
        </label>
        {file && (
          <Box sx={{ mt: 2 }}>
            <Typography>Selected: {file.name}</Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={uploadMutation.isPending}
              sx={{ mt: 1 }}
            >
              {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
            </Button>
          </Box>
        )}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      <Typography variant="h5" gutterBottom>
        Upload History
      </Typography>
      {queryError ? (
        <Alert severity="error">
          Failed to load upload history. Please try again.
        </Alert>
      ) : (
        <List>
          {uploads?.map((upload: any) => (
            <ListItem key={upload.id}>
              <ListItemText
                primary={upload.filename}
                secondary={new Date(upload.uploaded_at).toLocaleString()}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  )
}

export default UploadPage 