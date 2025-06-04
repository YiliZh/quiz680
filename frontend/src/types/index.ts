export interface Upload {
  id: number
  filename: string
  title: string
  description?: string
  file_path: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  processing_logs: string | null
  created_at: string
  updated_at: string
  user_id: number
  has_questions: boolean
} 