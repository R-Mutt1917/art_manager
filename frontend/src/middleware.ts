import { defineMiddleware } from 'astro:middleware';

// Red interna de Docker (el middleware corre en el server)
const API_URL = import.meta.env.API_URL ?? 'http://backend:8000';

// Matriz de protección: ruta → roles permitidos → a dónde redirigir si no
const RUTAS_PROTEGIDAS: { patron: RegExp; roles: string[]; redirect: string }[] = [
  { patron: /^\/inventario\/?$/,            roles: ['admin', 'curador', 'asesor'], redirect: '/catalogo' },
  { patron: /^\/dashboard\/?$/,             roles: ['admin', 'curador', 'asesor'], redirect: '/catalogo' },
  { patron: /^\/crear\/?$/,                 roles: ['admin', 'curador'],           redirect: '/catalogo' },
  { patron: /^\/tecnicas(\/.*)?$/,          roles: ['admin', 'curador'],           redirect: '/catalogo' },
  { patron: /^\/obras\/\d+\/editar\/?$/,    roles: ['admin', 'curador'],           redirect: '/inventario' },
];

export const onRequest = defineMiddleware(async (context, next) => {
  const path = context.url.pathname;
  const regla = RUTAS_PROTEGIDAS.find((r) => r.patron.test(path));

  // Ruta pública: seguir normal
  if (!regla) return next();

  // 1. Sin cookie → al login (guardando a dónde quería ir)
  const token = context.cookies.get('artmanager_token')?.value;
  if (!token) {
    return context.redirect(`/login?returnTo=${encodeURIComponent(path)}`);
  }

  // 2. Con cookie: preguntar al backend quién es y qué rol tiene
  try {
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
    });
    if (!res.ok) return context.redirect('/login');

    const me = await res.json();
    if (!regla.roles.includes(me.rol)) {
      return context.redirect(regla.redirect);
    }
  } catch {
    return context.redirect('/login');
  }

  return next();
});