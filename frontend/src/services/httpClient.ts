// Interceptor HTTP: adjunta el token automáticamente y maneja errores de auth.

import { getAccessToken, limpiarTokens } from './auth';

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Wrapper de fetch que:
 * 1. Adjunta el token de autenticación automáticamente
 * 2. Maneja errores 401/403 redirigiendo a /login
 * 3. Maneja errores de red de forma centralizada
 */
export async function httpClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();

  // Construir headers (merge con los que ya vengan)
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // Adjuntar token si existe
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Si no es FormData, agregar Content-Type JSON
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Manejar errores de autenticación
  if (response.status === 401 || response.status === 403) {
    limpiarTokens();
    window.location.href = '/login';
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