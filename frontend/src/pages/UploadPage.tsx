import { useState } from 'react'
import { Box, Button, Typography, Paper, List, ListItem, ListItemText } from '@mui/material'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'

function UploadPage() {
  const [file, setFile] = useState<File | null>(null)

  const { data: uploads, refetch } = useQuery({
    queryKey: ['uploads'],
    queryFn: async () => {
      const response = await axios.get('/api/uploads')
      return response.data
    }
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await axios.post('/api/uploads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    },
    onSuccess: () => {
      refetch()
      setFile(null)
    }
  })

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0])
    }
  }

  const handleUpload = () => {
    if (file) {
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
              Upload
            </Button>
          </Box>
        )}
      </Paper>

      <Typography variant="h5" gutterBottom>
        Upload History
      </Typography>
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
    </Box>
  )
}

export default UploadPage 