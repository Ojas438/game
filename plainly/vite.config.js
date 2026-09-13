import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite config for the Plainly React app, plus Vitest settings.
// Parser and calculator tests are pure JavaScript, so they run in a
// plain Node environment (no DOM needed).
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'node',
    include: ['src/**/*.test.js'],
  },
});
