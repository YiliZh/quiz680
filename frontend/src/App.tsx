import { Routes, Route } from 'react-router-dom'
import { Container } from '@mui/material'
import Navbar from './components/Navbar'
import UploadPage from './pages/UploadPage'
import HistoryPage from './pages/HistoryPage'
import QuizPage from './pages/QuizPage'
import AuthPage from './pages/AuthPage'
import ChapterList from './pages/ChapterList'
import ChapterDetail from './pages/ChapterDetail'
import PdfViewer from './pages/PdfViewer'

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
          <Route path="/uploads/:uploadId/chapters" element={<ChapterList />} />
          <Route path="/chapters/:chapterId" element={<ChapterDetail />} />
          <Route path="/pdf-viewer/:uploadId" element={<PdfViewer />} />
        </Routes>
      </Container>
    </>
  )
}

export default App 