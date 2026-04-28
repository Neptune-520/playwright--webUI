import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const proxyTarget = 'http://192.168.20.193:8001'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api/items': {
        target: proxyTarget,
        changeOrigin: true
      },
      '/api/folder': {
        target: proxyTarget,
        changeOrigin: true
      },
      '/api/upload': {
        target: proxyTarget,
        changeOrigin: true
      },
      '/api/search': {
        target: proxyTarget,
        changeOrigin: true
      },
      '/api/script-results': {
        target: proxyTarget,
        changeOrigin: true
      },
      '/api/config': {
        target: proxyTarget,
        changeOrigin: true
      }
    }
  }
})