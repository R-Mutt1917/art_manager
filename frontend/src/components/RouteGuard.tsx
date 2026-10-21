// Protección de rutas: si no hay token, redirige a /login.
// Se hidrata inmediatamente (client:only="react") para máxima seguridad.

import { useEffect } from 'react';

const ACCESS_TOKEN_KEY = 'artmanager_access_token';

interface RouteGuardProps {
  redirectTo?: string;
}

export default function RouteGuard({ redirectTo = '/login' }: RouteGuardProps) {
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      // Guardamos la URL original para redirigir después del login
      const returnTo = window.location.pathname + window.location.search;
      window.location.href = `${redirectTo}?returnTo=${encodeURIComponent(returnTo)}`;
    }
  }, [redirectTo]);

  // No renderiza nada visible
  return null;
}