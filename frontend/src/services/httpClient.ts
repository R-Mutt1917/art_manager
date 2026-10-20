// Interceptor HTTP: adjunta el token y maneja errores.
// SSR-Safe: elige la URL correcta según si corre en servidor o navegador.

import { getAccessToken, limpiarTokens } from './auth';

// 1. Detectar el entorno
const isServer = typeof window === 'undefined';

// 2. Elegir la URL correcta:
// - Servidor (Docker): usa la red interna 'http://backend:8000'
// - Cliente (Navegador): usa la URL pública 'http://localhost:8000'
const API_URL = isServer 
  ? (import.meta.env.API_URL || 'http://backend:8000') 
  : (import.meta.env.PUBLIC_API_URL || 'http://localhost:8000');

export async function httpClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // 3. Solo adjuntar token si estamos en el navegador (el servidor no tiene localStorage)
  if (!isServer) {
    const token = getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  // Si no es FormData, agregar Content-Type JSON
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  // 4. Hacer la petición a la URL correcta
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // 5. Manejar errores de autenticación (solo en cliente podemos redirigir)
  if (response.status === 401 || response.status === 403) {
    if (!isServer) {
      limpiarTokens();
      window.location.href = '/login';
    }
    throw new Error('Sesión expirada o sin permisos');
  }

  // Manejar errores del backend
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || `Error ${response.status}`);
  }

  // Si la respuesta es 204 (sin contenido), retornar null
  if (response.status === 204) {
    return null as T;
  }

  return await response.json();
}

// ==========================================
// Helpers específicos para cada método HTTP
// ==========================================

export const http = {
  get: <T = any>(endpoint: string) => httpClient<T>(endpoint, { method: 'GET' }),
  
  post: <T = any>(endpoint: string, body?: any) => 
    httpClient<T>(endpoint, { 
      method: 'POST', 
      body: body instanceof FormData ? body : JSON.stringify(body) 
    }),
  
  put: <T = any>(endpoint: string, body?: any) => 
    httpClient<T>(endpoint, { 
      method: 'PUT', 
      body: body instanceof FormData ? body : JSON.stringify(body) 
    }),
  
  delete: <T = any>(endpoint: string) => 
    httpClient<T>(endpoint, { method: 'DELETE' }),
};