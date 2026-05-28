import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/static/editor/',
  server: {
    port: 5173,
    proxy: {
      '/api/editor': 'http://localhost:8080',
      '/editor/export': 'http://localhost:8080',
    },
  },
  build: {
    outDir: '../app/ui/static/editor',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'main.js',
        chunkFileNames: 'chunk-[name].js',
        assetFileNames: (info) => info.name?.endsWith('.css') ? 'style.css' : '[name][extname]',
      },
    },
  },
})
