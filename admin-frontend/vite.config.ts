import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve('./src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    open: true,
    cors: true,
    hmr: {
      overlay: true
    }
  }
})
