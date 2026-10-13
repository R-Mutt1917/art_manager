// Obtenemos la URL del backend desde las variables de entorno
const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

// Interfaz que coincide con tu modelo de Obra en FastAPI
export interface Obra {
  id: number;
  titulo: string;
  anio: number;
  dimensiones: string;
  precio: number | null;
  estado: string;
  imagen_url: string | null;
}

/**
 * Obtiene todas las obras desde el backend.
 */
export async function getObras(): Promise<Obra[]> {
  try {
    const response = await fetch(`${API_URL}/obras/`);
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
    return []; // Retornamos array vacío para que la UI no se rompa
  }
}