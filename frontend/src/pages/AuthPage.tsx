import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Typography, Paper, TextField, Button, Alert } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import { useAuth } from '../contexts/AuthContext'

function AuthPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState<string>('')

  // Redirect to home if already authenticated
  useEffect(() => {
    if (user) {
      navigate('/')
    }
  }, [user, navigate])

  const authMutation = useMutation({
    mutationFn: async () => {
      console.log('Attempting auth with:', { email, username, isLogin })
      try {
        if (isLogin) {
          // For login, use FormData to match OAuth2PasswordRequestForm
          const formData = new FormData()
          formData.append('username', email) // Use email as username for login
          formData.append('password', password)
          const response = await api.post('/api/auth/login', formData, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          })
          return response.data
        } else {
          // For signup, use JSON
          const response = await api.post('/api/auth/signup', {
            email,
            username,
            password
          })
          return response.data
        }
      } catch (error: any) {
        console.error('Auth error:', error.response?.data || error.message)
        if (Array.isArray(error.response?.data?.detail)) {
          const errorMessages = error.response.data.detail.map((err: any) => err.msg).join(', ')
          throw new Error(errorMessages)
        }
        const errorDetail = error.response?.data?.detail || error.message || 'An error occurred'
        throw new Error(errorDetail)
      }
    },
    onSuccess: async (data) => {
      console.log('Auth successful:', data)
      if (isLogin) {
        localStorage.setItem('token', data.access_token)
        // Fetch user data after successful login
        try {
          const userResponse = await api.get('/api/auth/me')
          queryClient.setQueryData(['user'], userResponse.data)
        } catch (error) {
          console.error('Failed to fetch user data:', error)
        }
      }
      navigate('/')
    },
    onError: (error: Error) => {
      console.error('Auth mutation error:', error)
      setErrorMessage(error.message)
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