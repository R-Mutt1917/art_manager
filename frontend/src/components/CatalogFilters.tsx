import { useState, useEffect, useRef } from 'react';

interface Tecnica {
  id: number;
  nombre: string;
}

interface Filters {
  tecnica: string;
  estado: string;
  precio_min: string;
  precio_max: string;
  busqueda: string;
}

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

const fieldClass =
  'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white text-text-primary placeholder:text-gray-400 focus:ring-2 focus:ring-accent focus:border-accent outline-none transition';

const labelClass =
  'block text-[11px] font-semibold uppercase tracking-wider text-text-secondary mb-1.5';

export default function CatalogFilters() {
  const [tecnicas, setTecnicas] = useState<Tecnica[]>([]);
  const [filters, setFilters] = useState<Filters>({
    tecnica: '',
    estado: '',
    precio_min: '',
    precio_max: '',
    busqueda: '',
  });
  const [searchInput, setSearchInput] = useState('');
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/tecnicas/`)
      .then((res) => res.json())
      .then((data) => setTecnicas(data))
      .catch(() => console.error('Error cargando técnicas'));

    const params = new URLSearchParams(window.location.search);
    const initial = {
      tecnica: params.get('tecnica') || '',
      estado: params.get('estado') || '',
      precio_min: params.get('precio_min') || '',
      precio_max: params.get('precio_max') || '',
      busqueda: params.get('busqueda') || '',
    };
    setFilters(initial);
    setSearchInput(initial.busqueda);
  }, []);

  const applyFilters = (next: Filters) => {
    const params = new URLSearchParams();
    Object.entries(next).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    window.location.href = params.toString() ? `/?${params.toString()}` : '/';
  };

  // Selects: aplican al instante
  const handleChange = (key: keyof Filters, value: string) => {
    applyFilters({ ...filters, [key]: value });
  };

  // Inputs de texto/número: debounce de 600ms (no spamea el backend)
  const handleDebouncedChange = (key: keyof Filters, value: string) => {
    if (key === 'busqueda') setSearchInput(value);
    if (timerRef.current) window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => {
      applyFilters({ ...filters, [key]: value });
    }, 600);
  };

  const activeCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="mb-10">
      <div className="bg-white/90 backdrop-blur border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
        <div className="grid grid-cols-2 md:grid-cols-12 gap-3 items-end">
          {/* Buscar */}
          <div className="col-span-2 md:col-span-4">
            <label htmlFor="busqueda" className={labelClass}>Buscar</label>
            <div className="relative">
              <svg
                xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              >
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
              </svg>
              <input
                id="busqueda"
                type="text"
                value={searchInput}
                onChange={(e) => handleDebouncedChange('busqueda', e.target.value)}
                placeholder="Título o notas..."
                className={`${fieldClass} pl-9`}
              />
            </div>
          </div>

          {/* Técnica */}
          <div className="md:col-span-3">
            <label htmlFor="tecnica" className={labelClass}>Técnica</label>
            <select
              id="tecnica"
              value={filters.tecnica}
              onChange={(e) => handleChange('tecnica', e.target.value)}
              className={fieldClass}
            >
              <option value="">Todas</option>
              {tecnicas.map((t) => (
                <option key={t.id} value={t.id}>{t.nombre}</option>
              ))}
            </select>
          </div>

          {/* Estado */}
          <div className="md:col-span-2">
            <label htmlFor="estado" className={labelClass}>Estado</label>
            <select
              id="estado"
              value={filters.estado}
              onChange={(e) => handleChange('estado', e.target.value)}
              className={fieldClass}
            >
              <option value="">Todos</option>
              <option value="disponible">Disponible</option>
              <option value="vendida">Vendida</option>
              <option value="en_exposicion">En exposición</option>
              <option value="en_prestamo">En préstamo</option>
            </select>
          </div>

          {/* Precio */}
          <div className="md:col-span-2">
            <span className={labelClass}>Precio (ARS)</span>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                aria-label="Precio mínimo"
                value={filters.precio_min}
                onChange={(e) => handleDebouncedChange('precio_min', e.target.value)}
                placeholder="Mín"
                className={fieldClass}
              />
              <input
                type="number"
                aria-label="Precio máximo"
                value={filters.precio_max}
                onChange={(e) => handleDebouncedChange('precio_max', e.target.value)}
                placeholder="Máx"
                className={fieldClass}
              />
            </div>
          </div>

          {/* Limpiar (solo si hay filtros activos) */}
          <div className="md:col-span-1 flex md:justify-end">
            {activeCount > 0 && (
              <button
                onClick={() => applyFilters({ tecnica: '', estado: '', precio_min: '', precio_max: '', busqueda: '' })}
                className="text-sm font-medium text-text-secondary hover:text-red-600 transition whitespace-nowrap pb-2"
              >
                Limpiar ({activeCount})
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}