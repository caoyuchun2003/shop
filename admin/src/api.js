import axios from 'axios'
import { getToken } from './auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

api.interceptors.request.use((cfg) => {
  const token = getToken()
  if (token) cfg.headers['X-Admin-Token'] = token
  return cfg
})

export default api
