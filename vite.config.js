import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'remove-crossorigin',
      transformIndexHtml(html) {
        return html.replace(/crossorigin/g, '');
      }
    }
  ],
  base: "./",
  build: {
    sourcemap: false,
    minify: "esbuild",
    cssMinify: true,
    reportCompressedSize: false,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom"],
          sanscript: ["@indic-transliteration/sanscript"],
        },
      },
    },
  },
})
