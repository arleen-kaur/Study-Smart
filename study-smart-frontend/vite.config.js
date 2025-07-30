import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        if (
          warning.message &&
          warning.message.includes('Module level directives cause errors when bundled')
        ) {
          return;
        }
        warn(warning); 
      }
    }
  }
});
