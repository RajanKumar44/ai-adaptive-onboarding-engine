import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  refresh: (data) => apiClient.post('/auth/refresh', data),
  logout: () => apiClient.post('/auth/logout'),
  getProfile: () => apiClient.get('/auth/me'),
  changePassword: (data) => apiClient.post('/auth/change-password', data),
}

export const analysisAPI = {
  analyze: (formData) => apiClient.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getAnalysis: (id) => apiClient.get(`/analysis/${id}`),
  listAnalyses: (userId, params) => apiClient.get(`/users/${userId}/analyses`, { params }),
}

export const adminAPI = {
  listUsers: (params) => apiClient.get('/admin/users', { params }),
  getUserDetails: (id) => apiClient.get(`/admin/users/${id}`),
  updateUser: (id, data) => apiClient.put(`/admin/users/${id}`, data),
  deleteUser: (id) => apiClient.delete(`/admin/users/${id}`),
}

export const metricsAPI = {
  getHealth: () => apiClient.get('/metrics/health'),
  getPrometheus: () => apiClient.get('/metrics/prometheus'),
  getPerformance: () => apiClient.get('/metrics/performance'),
}

export const llmAPI = {
  extractSkills: (data) => apiClient.post('/llm/extract-skills', data),
  generateText: (data) => apiClient.post('/llm/generate-text', data),
  validateProviders: () => apiClient.get('/llm/providers/validate'),
}

export default apiClient
