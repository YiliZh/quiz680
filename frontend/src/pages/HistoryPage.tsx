import { useQuery } from '@tanstack/react-query'
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material'
import axios from 'axios'

function HistoryPage() {
  const { data: attempts } = useQuery({
    queryKey: ['attempts'],
    queryFn: async () => {
      const response = await axios.get('/api/history/attempts')
      return response.data
    }
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Quiz History
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Question</TableCell>
              <TableCell>Your Answer</TableCell>
              <TableCell>Correct</TableCell>
              <TableCell>Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {attempts?.map((attempt: any) => (
              <TableRow key={attempt.id}>
                <TableCell>{attempt.question.q_text}</TableCell>
                <TableCell>{attempt.chosen_idx}</TableCell>
                <TableCell>{attempt.is_correct ? 'Yes' : 'No'}</TableCell>
                <TableCell>{new Date(attempt.attempted_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default HistoryPage 