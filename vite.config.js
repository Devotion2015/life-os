import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'copy-404',
      closeBundle() {
        const src = path.join(__dirname, 'dist', 'index.html')
        const dest = path.join(__dirname, 'dist', '404.html')
        fs.copyFileSync(src, dest)
      }
    }
  ],
  base: '/life-os/',
})
