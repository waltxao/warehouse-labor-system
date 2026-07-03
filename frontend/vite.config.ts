import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // 构建产物输出到后端静态目录，供 FastAPI StaticFiles 托管
    outDir: '../backend/app/static',
    emptyOutDir: true,
  },
})
