// Servicio centralizado de autenticación: login, logout y manejo de tokens.

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

// Claves únicas para localStorage (prefijadas para evitar colisiones)
const ACCESS_TOKEN_KEY = 'artmanager_access_token';
const REFRESH_TOKEN_KEY = 'artmanager_refresh_token';
const COOKIE_TOKEN_KEY = 'artmanager_token'; // Para compatibilidad con el backend, que también puede usar cookies

// ==========================================
// Tipos
// ==========================================

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ==========================================
// Manejo de tokens en localStorage
// ==========================================

/** Guarda el par de tokens después de un login exitoso. */
export function guardarTokens(tokens: LoginResponse): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  // ← NUEVO: Guardar en cookie para que Astro SSR pueda leerlo
  // max-age=86400 es 24 horas. SameSite=Lax es seguro para navegación normal.
  document.cookie = `${COOKIE_TOKEN_KEY}=${tokens.access_token}; path=/; max-age=86400; SameSite=Lax`;
}

/** Devuelve el access token actual, o null si no hay sesión. */
export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/** Devuelve el refresh token actual, o null si no hay sesión. */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/** Borra ambos tokens (logout). */
export function limpiarTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  // ← NUEVO: Borrar la cookie también
  document.cookie = `${COOKIE_TOKEN_KEY}=; path=/; max-age=0; SameSite=Lax`;
}

/** ¿Hay una sesión activa? (solo verifica presencia del token, no su validez). */
export function estaAutenticado(): boolean {
  return getAccessToken() !== null;
}

// ==========================================
// Llamadas a la API
// ==========================================

/**
 * Autentica al usuario contra POST /auth/login.
 * Si tiene éxito, guarda los tokens y los devuelve.
 * Si falla, lanza un Error con el mensaje del backend.
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Credenciales inválidas');
  }

  const tokens: LoginResponse = await response.json();
  guardarTokens(tokens);
  return tokens;
}

/** Cierra la sesión: borra tokens y vuelve al catálogo. */
export function logout(): void {
  limpiarTokens();
  window.location.href = '/';
}