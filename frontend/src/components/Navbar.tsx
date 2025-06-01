import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Quiz System
        </Typography>
        <Box>
          <Button color="inherit" component={RouterLink} to="/">
            Upload
          </Button>
          <Button color="inherit" component={RouterLink} to="/history">
            History
          </Button>
          <Button color="inherit" component={RouterLink} to="/auth">
            Login
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar 