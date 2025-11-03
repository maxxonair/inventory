import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import autoprefixer from 'autoprefixer';
import tailwindcss from 'tailwindcss';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 3000
  },
  css: {
    postcss: {
      plugins: [tailwindcss(), autoprefixer()]
    }
  },
  build: {
    cssCodeSplit: true,
    // Limit parrallel file operations required to be able to build in 
    // containers with limited resources
    rollupOptions: {
      maxParallelFileOps: 100
    }
  }
});
