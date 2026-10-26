// @ts-check
import { defineConfig, envField } from 'astro/config';
import react from '@astrojs/react';
import node from '@astrojs/node';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  integrations: [react()],
  
  // Definimos las variables de entorno que ya usas en docker-compose.yml
  env: {
    schema: {
      PUBLIC_API_URL: envField.string({ 
        context: 'client', 
        access: 'public', 
        default: 'http://localhost:8000' 
      }),
      API_URL: envField.string({ 
        context: 'server', 
        access: 'secret', 
        default: 'http://backend:8000' 
      }),
    },
  },

  vite: {
    plugins: [tailwindcss()]
  },
  devToolbar: {
    enabled: false
  }
});