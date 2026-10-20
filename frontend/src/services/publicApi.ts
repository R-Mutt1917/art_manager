// Servicio para el catálogo público (sin datos sensibles).
// Aplica el principio Interface Segregation (SOLID):
// - PublicObra: solo campos visibles para visitantes
// - PrivateObra (ya existe en api.ts): todos los campos para usuarios logueados

import { http } from './httpClient';

// ==========================================
// Interfaces públicas (datos no sensibles)
// ==========================================

export interface PublicObra {
  id: number;
  titulo: string;
  anio: number;
  tecnica_id: number | null;
  estado: string;
  // ⚠️ Intencionalmente NO incluye:
  // - precio (dato comercial sensible)
  // - imagen_url (protección de derechos de autor)
  // - dimensiones (dato técnico sensible)
  // - notas (información curatorial privada)
  // - comprador_id (privacidad del comprador)
}

export interface PublicTecnica {
  id: number;
  nombre: string;
  descripcion: string | null;
}

// ==========================================
// Endpoints públicos (no requieren auth)
// ==========================================

/**
 * Obtiene el catálogo público (sin datos sensibles).
 * Este endpoint NO requiere autenticación.
 */
export async function getObrasPublicas(): Promise<PublicObra[]> {
  return http.get<PublicObra[]>('/obras/publicas');
}

/**
 * Obtiene todas las técnicas (para mostrar nombres en el catálogo).
 * Las técnicas son públicas (no hay datos sensibles).
 */
export async function getTecnicasPublicas(): Promise<PublicTecnica[]> {
  return http.get<PublicTecnica[]>('/tecnicas/');
}