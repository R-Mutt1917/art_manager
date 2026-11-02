// Servicio ÚNICO de datos públicos (sin autenticación).
// Server-side (Astro SSR en Docker): red interna (API_URL)
// Client-side (navegador): localhost publicado (PUBLIC_API_URL)
const API_URL = import.meta.env.SSR 
  ? import.meta.env.API_URL 
  : import.meta.env.PUBLIC_API_URL;

// ==========================================
// Catálogo público (Interface Segregation - SOLID)
// ==========================================
export interface PublicObra {
  id: number;
  titulo: string;
  anio: number;
  tecnica_id: number | null;
  estado: string;
  imagen_url: string | null;
  statement: string | null;
  // ⚠️ Intencionalmente NUNCA: precio, dimensiones, notas, comprador_id
}

export interface PublicTecnica {
  id: number;
  nombre: string;
  descripcion: string | null;
}

// ==========================================
// Galerías y artistas públicos
// ==========================================
export interface ObraPublic {
  id: number;
  titulo: string;
  anio: number;
  estado: string;
  imagen_url: string | null;
  tecnica_nombre: string | null;
  statement: string | null;
}

export interface ArtistaPublic {
  id: number;
  nombre: string;
  slug: string;
  bio: string | null;
  nacionalidad: string | null;
  anio_nacimiento: number | null;
  foto_perfil: string | null;
  sitio_web: string | null;
}

export interface ArtistaDetallePublic extends ArtistaPublic {
  obras: ObraPublic[];
}

export interface GaleriaPublic {
  id: number;
  nombre: string;
  slug: string;
  bio: string | null;
  ubicacion: string | null;
  sitio_web: string | null;
  logo_url: string | null;
  total_artistas: number;
  total_obras: number;
}

async function fetchPublic<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export const apiPublic = {
  // Catálogo
  getObrasPublicas: (filtros?: Record<string, string | null>) => {
    const params = new URLSearchParams();
    Object.entries(filtros ?? {}).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    const qs = params.toString();
    return fetchPublic<PublicObra[]>(`/obras/publicas${qs ? `?${qs}` : ''}`);
  },

  getTecnicasPublicas: () => fetchPublic<PublicTecnica[]>('/tecnicas/'),

  // Galerías y artistas
  getGaleria: (slug: string) =>
    fetchPublic<GaleriaPublic>(`/galerias/${slug}`),

  getArtistas: (galeriaSlug: string) =>
    fetchPublic<ArtistaPublic[]>(`/galerias/${galeriaSlug}/artistas`),

  getArtista: (galeriaSlug: string, artistaSlug: string) =>
    fetchPublic<ArtistaDetallePublic>(
      `/galerias/${galeriaSlug}/artistas/${artistaSlug}`
    ),
};