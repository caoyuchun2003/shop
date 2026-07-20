import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

api.interceptors.request.use((cfg) => {
  cfg.headers['X-Admin-Token'] = localStorage.getItem('ADMIN_TOKEN') || 'dev-admin'
  return cfg
})

export default api
