// Obtenemos la URL del backend desde las variables de entorno
const API_URL = import.meta.env.API_URL || import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

// ==========================================
// INTERFACES (definen la forma de los datos)
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
// FUNCIONES DE OBRAS
// ==========================================

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

// ==========================================
// FUNCIONES DE TÉCNICAS
// ==========================================

/**
 * Obtiene una técnica por su ID.
 */
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

/**
 * Obtiene todas las técnicas del catálogo.
 */
export async function getTecnicas(): Promise<Tecnica[]> {
  try {
    const response = await fetch(`${API_URL}/tecnicas/`);
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.error("Error fetching tecnicas:", error);
    return [];
  }
}

// ==========================================
// FUNCIONES DE COMPRADORES
// ==========================================

/**
 * Obtiene un comprador por su ID.
 */
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