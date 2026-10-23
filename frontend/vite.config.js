import { resolve } from 'path';

export default {
  root: '.',
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        overview: resolve(__dirname, 'overview.html'),
        incident: resolve(__dirname, 'incident.html'),
        recovery: resolve(__dirname, 'recovery.html'),
        fleet: resolve(__dirname, 'fleet.html'),
        analytics: resolve(__dirname, 'analytics.html'),
        settings: resolve(__dirname, 'settings.html'),
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
};

