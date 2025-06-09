import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/auth')
  }

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Quiz System
        </Typography>
        <Box>
          {user ? (
            <>
              <Typography variant="body1" component="span" sx={{ mr: 2 }}>
                Welcome, {user.username}
              </Typography>
              <Button color="inherit" component={RouterLink} to="/">
                Upload
              </Button>
              <Button color="inherit" component={RouterLink} to="/history">
                History
              </Button>
              <Button color="inherit" component={RouterLink} to="/exam-history">
                Exam History
              </Button>
              <Button color="inherit" onClick={handleLogout}>
                Logout
              </Button>
            </>
          ) : (
            <Button color="inherit" component={RouterLink} to="/auth">
              Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar 