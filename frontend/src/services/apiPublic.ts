// Server-side (Astro SSR en Docker): usa la red interna de Docker
// Client-side (Navegador): usa localhost publicado
const API_URL = import.meta.env.SSR 
  ? import.meta.env.API_URL 
  : import.meta.env.PUBLIC_API_URL;

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
  getGaleria: (slug: string) =>
    fetchPublic<GaleriaPublic>(`/galerias/${slug}`),

  getArtistas: (galeriaSlug: string) =>
    fetchPublic<ArtistaPublic[]>(`/galerias/${galeriaSlug}/artistas`),

  getArtista: (galeriaSlug: string, artistaSlug: string) =>
    fetchPublic<ArtistaDetallePublic>(
      `/galerias/${galeriaSlug}/artistas/${artistaSlug}`
    ),
};