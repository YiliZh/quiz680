import { Routes, Route } from 'react-router-dom'
import { Container } from '@mui/material'
import Navbar from './components/Navbar'
import UploadPage from './pages/UploadPage'
import HistoryPage from './pages/HistoryPage'
import QuizPage from './pages/QuizPage'
import AuthPage from './pages/AuthPage'

function App() {
  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/quiz/:chapterId" element={<QuizPage />} />
          <Route path="/auth" element={<AuthPage />} />
        </Routes>
      </Container>
    </>
  )
}

export default App 