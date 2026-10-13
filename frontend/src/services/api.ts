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
  tecnica_id: number | null;
  comprador_id: number | null;
  notas: string | null;
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

/**
 * Obtiene una obra específica por su ID desde el backend.
 */
export async function getObraById(id: number): Promise<Obra | null> {
  try {
    const response = await fetch(`${API_URL}/obras/${id}`);
    
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error al obtener la obra ${id}:`, error);
    return null;
  }
}

// Nuevas interfaces para los datos relacionados
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

// 2. Función para obtener una técnica por su ID
export async function getTecnica(id: number): Promise<Tecnica | null> {
  try {
    const response = await fetch(`${API_URL}/tecnicas/${id}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error al obtener técnica ${id}:`, error);
    return null;
  }
}

// 3. Función para obtener un comprador por su ID
export async function getComprador(id: number): Promise<Comprador | null> {
  try {
    const response = await fetch(`${API_URL}/compradores/${id}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error al obtener comprador ${id}:`, error);
    return null;
  }
}