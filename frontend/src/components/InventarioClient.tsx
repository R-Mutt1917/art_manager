// Componente React que carga el catálogo privado del lado del cliente.
// Verifica autenticación y aplica filtros avanzados.

import { useState, useEffect } from 'react';
import { http } from '../services/httpClient';
import { estaAutenticado } from '../services/auth';

// ==========================================
// Interfaces
// ==========================================

interface Obra {
  id: number;
  titulo: string;
  anio: number;
  dimensiones: string;
  precio: number | null;
  estado: string;
  imagen_url: string | null;
  tecnica_id: number | null;
  notas: string | null;
}

interface Tecnica {
  id: number;
  nombre: string;
}

// ==========================================
// Componente
// ==========================================

export default function InventarioClient() {
  const [obras, setObras] = useState<Obra[]>([]);
  const [tecnicas, setTecnicas] = useState<Tecnica[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Filtros
  const [filtroTecnica, setFiltroTecnica] = useState<string>('');
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [filtroBusqueda, setFiltroBusqueda] = useState<string>('');

  // Al montar: verificar auth y cargar datos
  useEffect(() => {
    const auth = estaAutenticado();
    setIsAuthenticated(auth);

    if (!auth) {
      setLoading(false);
      return;
    }

    // Cargar técnicas para el filtro
    http.get<Tecnica[]>('/tecnicas/')
      .then((data) => setTecnicas(data))
      .catch((err) => console.error('Error al cargar técnicas:', err));

    // Cargar obras
    cargarObras();
  }, []);

  // Recargar obras cuando cambian los filtros
  useEffect(() => {
    if (isAuthenticated) {
      cargarObras();
    }
  }, [filtroTecnica, filtroEstado, filtroBusqueda]);

  const cargarObras = async () => {
    setLoading(true);
    setError(null);

    try {
      // Construir query params
      const params = new URLSearchParams();
      if (filtroTecnica) params.set('tecnica_id', filtroTecnica);
      if (filtroEstado) params.set('estado', filtroEstado);
      if (filtroBusqueda) params.set('busqueda', filtroBusqueda);

      const queryString = params.toString();
      const endpoint = queryString ? `/obras/?${queryString}` : '/obras/';

      const data = await http.get<Obra[]>(endpoint);
      setObras(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar obras');
    } finally {
      setLoading(false);
    }
  };

  const limpiarFiltros = () => {
    setFiltroTecnica('');
    setFiltroEstado('');
    setFiltroBusqueda('');
  };

  // ==========================================
  // Render
  // ==========================================

  if (!isAuthenticated) {
    return (
      <div className="text-center py-20 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <svg xmlns="http://www.w3.org/2000/svg" className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <h3 className="font-serif text-2xl font-bold text-text-primary mb-2">
          Acceso restringido
        </h3>
        <p className="text-text-secondary mb-6">
          Inicia sesión para ver el inventario completo con precios e imágenes HD.
        </p>
        <a
          href="/login"
          className="inline-block px-6 py-3 bg-accent text-white font-semibold rounded-lg hover:bg-accent/90 transition-colors"
        >
          Iniciar Sesión
        </a>
      </div>
    );
  }

  if (loading) {
    return <div className="text-center py-12 text-text-secondary">Cargando inventario...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        <p>{error}</p>
        <button onClick={cargarObras} className="mt-4 text-accent hover:underline">
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Filtros */}
      <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Búsqueda */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Buscar
            </label>
            <input
              type="text"
              value={filtroBusqueda}
              onChange={(e) => setFiltroBusqueda(e.target.value)}
              placeholder="Título o notas..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-accent focus:border-accent outline-none"
            />
          </div>

          {/* Técnica */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Técnica
            </label>
            <select
              value={filtroTecnica}
              onChange={(e) => setFiltroTecnica(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-accent focus:border-accent outline-none"
            >
              <option value="">Todas</option>
              {tecnicas.map((t) => (
                <option key={t.id} value={t.id.toString()}>
                  {t.nombre}
                </option>
              ))}
            </select>
          </div>

          {/* Estado */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Estado
            </label>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-accent focus:border-accent outline-none"
            >
              <option value="">Todos</option>
              <option value="disponible">Disponible</option>
              <option value="vendida">Vendida</option>
              <option value="en_exposicion">En exposición</option>
              <option value="en_prestamo">En préstamo</option>
            </select>
          </div>

          {/* Limpiar */}
          <div className="flex items-end">
            <button
              onClick={limpiarFiltros}
              className="w-full px-4 py-2 text-sm font-medium text-text-secondary border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      {/* Lista de obras */}
      {obras.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {obras.map((obra) => (
            <ObraCard key={obra.id} obra={obra} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
          <p className="text-text-secondary text-lg">
            No hay obras que coincidan con los filtros seleccionados.
          </p>
          <button onClick={limpiarFiltros} className="mt-4 text-accent hover:underline">
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}

// ==========================================
// Subcomponente: Tarjeta de obra privada
// ==========================================

function ObraCard({ obra }: { obra: Obra }) {
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
  const imagenSrc = obra.imagen_url ? `${API_URL}${obra.imagen_url}` : null;

  const estadoLegible = {
    disponible: 'Disponible',
    vendida: 'Vendida',
    en_exposicion: 'En exposición',
    en_prestamo: 'En préstamo',
  }[obra.estado] || obra.estado;

  return (
    <a
      href={`/obras/${obra.id}`}
      className="group block bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow border border-gray-100"
    >
      {imagenSrc ? (
        <img
          src={imagenSrc}
          alt={obra.titulo}
          className="w-full aspect-[4/3] object-cover"
          loading="lazy"
        />
      ) : (
        <div className="w-full aspect-[4/3] bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-16 h-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      )}

      <div className="p-5">
        <h3 className="font-serif text-lg font-bold text-text-primary mb-2 group-hover:text-accent transition-colors">
          {obra.titulo}
        </h3>
        <p className="text-sm text-text-secondary mb-3">{obra.anio}</p>
        
        {obra.precio && (
          <p className="text-lg font-bold text-accent mb-3">
            ${obra.precio.toLocaleString('es-AR')}
          </p>
        )}

        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <span className="text-xs font-medium px-2 py-1 rounded-full bg-gray-100 text-text-secondary">
            {estadoLegible}
          </span>
          <span className="text-xs text-accent font-medium">
            Ver detalles →
          </span>
        </div>
      </div>
    </a>
  );
}