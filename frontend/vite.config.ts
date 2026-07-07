import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  // Must match the repo name so GitHub Pages (served from
  // https://<user>.github.io/B-rs/) resolves asset URLs correctly.
  base: '/B-rs/',
  plugins: [react()],
})
