import { useQuery, useMutation } from '@tanstack/react-query'
import api from './axios'
import { Upload } from '../types'

export const useUploads = () => {
  return api.get<Upload[]>('/api/uploads').then(response => response.data);
}

export const useUploadFile = () => {
  return useMutation({
    mutationFn: async (formData: FormData) => {
      // Get the file name without extension for the title
      const file = formData.get('file') as File;
      const title = file.name.replace(/\.[^/.]+$/, ""); // Remove file extension
      
      // Add title to formData
      formData.append('title', title);
      
      const response = await api.post<Upload>('/api/uploads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
  });
}

export const useQuestions = (chapterId: string) => {
  return useQuery({
    queryKey: ['questions', chapterId],
    queryFn: async () => {
      const response = await api.get(`/api/questions/${chapterId}/questions`)
      return response.data
    }
  })
}

export const useSubmitAnswer = () => {
  return useMutation({
    mutationFn: async ({ questionId, chosenIdx }: { questionId: number; chosenIdx: number }) => {
      const response = await api.post(`/api/questions/${questionId}/answer`, { chosen_idx: chosenIdx })
      return response.data
    }
  })
}

export const useAttempts = () => {
  return useQuery({
    queryKey: ['attempts'],
    queryFn: async () => {
      const response = await api.get('/api/history')
      return response.data
    }
  })
}

export const useAuth = (isLogin: boolean) => {
  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const response = await api.post(`/api/auth/${isLogin ? 'login' : 'signup'}`, {
        email,
        password
      })
      return response.data
    }
  })
} 