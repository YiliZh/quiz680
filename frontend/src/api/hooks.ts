import { useQuery, useMutation } from '@tanstack/react-query'
import api from './axios'

export const useUploads = () => {
  return useQuery({
    queryKey: ['uploads'],
    queryFn: async () => {
      const response = await api.get('/uploads')
      return response.data
    }
  })
}

export const useUploadFile = () => {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/uploads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    }
  })
}

export const useQuestions = (chapterId: string) => {
  return useQuery({
    queryKey: ['questions', chapterId],
    queryFn: async () => {
      const response = await api.get(`/questions/${chapterId}/questions`)
      return response.data
    }
  })
}

export const useSubmitAnswer = () => {
  return useMutation({
    mutationFn: async ({ questionId, chosenIdx }: { questionId: number; chosenIdx: number }) => {
      const response = await api.post(`/questions/${questionId}/answer`, { chosen_idx: chosenIdx })
      return response.data
    }
  })
}

export const useAttempts = () => {
  return useQuery({
    queryKey: ['attempts'],
    queryFn: async () => {
      const response = await api.get('/history/attempts')
      return response.data
    }
  })
}

export const useAuth = (isLogin: boolean) => {
  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const response = await api.post(`/auth/${isLogin ? 'login' : 'signup'}`, {
        email,
        password
      })
      return response.data
    }
  })
} 