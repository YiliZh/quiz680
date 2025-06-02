import axios, { AxiosError } from 'axios';

// Types
export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

export interface Chapter {
  id: number;
  chapter_no: number;
  title: string;
  summary: string;
  keywords: string[];
  content: string;
  upload_id: number;
  created_at: string;
}

export interface Upload {
  id: number;
  filename: string;
  status: string;
  created_at: string;
  chapters?: Chapter[];
}

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token and logging
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
    params: config.params,
    data: config.data,
  });
  return config;
});

// Add response interceptor to handle errors and logging
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      data: response.data,
    });
    return response;
  },
  (error: AxiosError) => {
    console.error('[API Error]', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// API Service methods
export const apiService = {
  // Auth
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (email: string, password: string) => {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  },

  // Uploads
  getUploads: async () => {
    const response = await api.get<Upload[]>('/uploads');
    return response.data;
  },

  createUpload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<Upload>('/uploads', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Chapters
  getChapters: async (uploadId: number, page: number = 1, pageSize: number = 10) => {
    const response = await api.get<{ items: Chapter[]; total: number }>(`/uploads/${uploadId}/chapters`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getChapter: async (chapterId: number) => {
    const response = await api.get<Chapter>(`/chapters/${chapterId}`);
    return response.data;
  },

  // Quiz
  generateQuiz: async (chapterId: number) => {
    const response = await api.post(`/chapters/${chapterId}/quiz`);
    return response.data;
  },

  submitQuiz: async (chapterId: number, answers: Record<string, string>) => {
    const response = await api.post(`/chapters/${chapterId}/quiz/submit`, { answers });
    return response.data;
  },
};

export { api }; 