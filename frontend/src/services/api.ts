// Obtenemos la URL del backend desde las variables de entorno
const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export interface Artwork {
  id: number;
  titulo: string;
  anio: number;
  dimensiones: string;
  precio: number | null;
  estado: string;
  imagen_url: string | null;
  tecnica_id: number | null;
}

/**
 * Obtiene todas las obras disponibles.
 * En el futuro, aquí agregaremos paginación y filtros.
 */
export async function getArtworks(): Promise<Artwork[]> {
  try {
    const response = await fetch(`${API_URL}/obras/?estado=disponible`);
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error al obtener obras:", error);
    return []; // Retornamos array vacío para que la UI no se rompa, pero mostraremos un estado de error luego
  }
}

/**
 * Obtiene una obra específica por su ID.
 */
export async function getArtworkById(id: number): Promise<Artwork | null> {
  try {
    const response = await fetch(`${API_URL}/obras/${id}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error al obtener la obra ${id}:`, error);
    return null;
  }
}