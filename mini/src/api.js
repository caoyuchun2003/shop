import axios from 'axios'

const SESSION_KEY = 'shop_sid'

function sessionId() {
  let sid = localStorage.getItem(SESSION_KEY)
  if (!sid) {
    sid = crypto.randomUUID().replace(/-/g, '')
    localStorage.setItem(SESSION_KEY, sid)
  }
  return sid
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
})

api.interceptors.request.use((cfg) => {
  cfg.headers['X-Session-Id'] = sessionId()
  return cfg
})

export default api
