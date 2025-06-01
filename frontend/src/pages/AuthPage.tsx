import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Typography, Paper, TextField, Button, Alert } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'

function AuthPage() {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const authMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/auth/${isLogin ? 'login' : 'signup'}`, {
        email,
        password
      })
      return response.data
    },
    onSuccess: (data) => {
      if (isLogin) {
        localStorage.setItem('token', data.access_token)
      }
      navigate('/')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
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
        {authMutation.isError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {authMutation.error instanceof Error ? authMutation.error.message : 'An error occurred'}
          </Alert>
        )}
      </Paper>
    </Box>
  )
}

export default AuthPage 