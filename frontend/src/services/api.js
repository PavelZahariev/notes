import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

import { supabase } from './supabase'

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  async (config) => {
    // Get auth token from Supabase session
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: Handle API errors
    return Promise.reject(error)
  }
)

// Voice API
export const voiceAPI = {
  transcribe: async (audioFile) => {
    const formData = new FormData()
    formData.append('file', audioFile)
    const response = await apiClient.post('/api/voice/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  process: async (audioFile) => {
    const formData = new FormData()
    formData.append('file', audioFile)
    const response = await apiClient.post('/api/voice/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

// Notes API
export const notesAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/api/notes', {
      params: { skip, limit },
    })
    return response.data
  },
  getById: async (noteId) => {
    const response = await apiClient.get(`/api/notes/${noteId}`)
    return response.data
  },
  create: async (note) => {
    const response = await apiClient.post('/api/notes', note)
    return response.data
  },
  update: async (noteId, note) => {
    const response = await apiClient.put(`/api/notes/${noteId}`, note)
    return response.data
  },
  delete: async (noteId) => {
    const response = await apiClient.delete(`/api/notes/${noteId}`)
    return response.data
  },
}

// Reminders API
export const remindersAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/api/reminders', {
      params: { skip, limit },
    })
    return response.data
  },
  getById: async (reminderId) => {
    const response = await apiClient.get(`/api/reminders/${reminderId}`)
    return response.data
  },
  create: async (reminder) => {
    const response = await apiClient.post('/api/reminders', reminder)
    return response.data
  },
  update: async (reminderId, reminder) => {
    const response = await apiClient.put(`/api/reminders/${reminderId}`, reminder)
    return response.data
  },
  delete: async (reminderId) => {
    const response = await apiClient.delete(`/api/reminders/${reminderId}`)
    return response.data
  },
}

export default apiClient

