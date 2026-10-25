// Servicio de obras, técnicas y compradores usando el interceptor HTTP.

import { http } from './httpClient';

// ==========================================
// Interfaces
// ==========================================

export interface Obra {
  id: number;
  titulo: string;
  anio: number;
  dimensiones: string;
  precio: number | null;
  estado: string;
  imagen_url: string | null;
  tecnica_id: number | null;
  comprador_id: number | null;
  notas: string | null;
  statement: string | null;  // ← NUEVO: texto curatorial público
}

export interface Tecnica {
  id: number;
  nombre: string;
  descripcion: string | null;
}

export interface Comprador {
  id: number;
  nombre: string;
  email: string | null;
}

// ==========================================
// Obras
// ==========================================

export async function getObras(): Promise<Obra[]> {
  return http.get<Obra[]>('/obras/');
}

export async function getObraById(id: number): Promise<Obra | null> {
  try {
    return await http.get<Obra>(`/obras/${id}`);
  } catch {
    return null;
  }
}

// ==========================================
// Técnicas
// ==========================================

export async function getTecnicas(): Promise<Tecnica[]> {
  return http.get<Tecnica[]>('/tecnicas/');
}

export async function getTecnica(id: number): Promise<Tecnica | null> {
  try {
    return await http.get<Tecnica>(`/tecnicas/${id}`);
  } catch {
    return null;
  }
}

// ==========================================
// Compradores
// ==========================================

export async function getComprador(id: number): Promise<Comprador | null> {
  try {
    return await http.get<Comprador>(`/compradores/${id}`);
  } catch {
    return null;
  }
}