import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: process.env.VITE_BASE || '/',
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:8020', '/health': 'http://127.0.0.1:8020' } },
})
