import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Typography, Paper, TextField, Button, Alert } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import api from '../api/axios'

function AuthPage() {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState<string>('')

  const authMutation = useMutation({
    mutationFn: async () => {
      console.log('Attempting auth with:', { email, username, isLogin })
      try {
        const response = await api.post(`/auth/${isLogin ? 'login' : 'signup'}`, {
          email,
          username,
          password
        })
        console.log('Auth response:', response.data)
        return response.data
      } catch (error: any) {
        console.error('Auth error:', error.response?.data || error.message)
        throw error
      }
    },
    onSuccess: (data) => {
      console.log('Auth successful:', data)
      if (isLogin) {
        localStorage.setItem('token', data.access_token)
      }
      navigate('/')
    },
    onError: (error: any) => {
      console.error('Auth mutation error:', error)
      setErrorMessage(error.response?.data?.detail || error.message || 'An error occurred')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')
    console.log('Submitting form:', { email, username, isLogin })
    authMutation.mutate()
  }

  return (
    <Box sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        {isLogin ? 'Login' : 'Sign Up'}
      </Typography>
      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            margin="normal"
            required
          />
          {!isLogin && (
            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
            />
          )}
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
          />
          <Button
            fullWidth
            variant="contained"
            type="submit"
            disabled={authMutation.isPending}
            sx={{ mt: 2 }}
          >
            {isLogin ? 'Login' : 'Sign Up'}
          </Button>
        </form>
        <Button
          fullWidth
          onClick={() => setIsLogin(!isLogin)}
          sx={{ mt: 1 }}
        >
          {isLogin ? 'Need an account? Sign Up' : 'Already have an account? Login'}
        </Button>
        {errorMessage && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errorMessage}
          </Alert>
        )}
      </Paper>
    </Box>
  )
}

export default AuthPage 