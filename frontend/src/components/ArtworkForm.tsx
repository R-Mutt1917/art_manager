import { useState, useEffect, type FormEvent, type ChangeEvent } from 'react';
import { http } from '../services/httpClient'; // ← NUEVO: Usamos el interceptor

interface Tecnica { id: number; nombre: string; }

interface ArtworkFormProps {
  initialData?: {
    id: number;
    titulo: string;
    anio: number;
    dimensiones: string;
    precio: number | null;
    notas: string | null;
    estado: string;
    tecnica_nombre: string;
    imagen_url: string | null;
  };
}

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export default function ArtworkForm({ initialData }: ArtworkFormProps) {
  const isEditMode = !!initialData;

  const [tecnicas, setTecnicas] = useState<Tecnica[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [tecnicaInput, setTecnicaInput] = useState(initialData?.tecnica_nombre ?? '');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [imagen, setImagen] = useState<File | null>(null);

  const [formData, setFormData] = useState({
    titulo: initialData?.titulo ?? '',
    anio: initialData?.anio?.toString() ?? new Date().getFullYear().toString(),
    dimensiones: initialData?.dimensiones ?? '',
    precio: initialData?.precio?.toString() ?? '',
    notas: initialData?.notas ?? '',
  });

  // Cargar técnicas usando el interceptor
  useEffect(() => {
    http.get<Tecnica[]>('/tecnicas/')
      .then((data) => setTecnicas(data))
      .catch((err) => setError(err.message));
  }, []);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setImagen(e.target.files[0]);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!tecnicaInput.trim()) {
      setError('La técnica es requerida');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const data = new FormData();
      data.append('titulo', formData.titulo);
      data.append('anio', formData.anio);
      data.append('dimensiones', formData.dimensiones);
      if (formData.precio) data.append('precio', formData.precio);
      if (formData.notas) data.append('notas', formData.notas);
      data.append('tecnica', tecnicaInput);
      if (imagen) data.append('imagen', imagen);

      // ← NUEVO: Usamos el interceptor que adjunta el token automáticamente
      const response = isEditMode
        ? await http.put(`/obras/${initialData!.id}`, data)
        : await http.post('/obras/', data);

      setSuccess(true);

      if (isEditMode) {
        setTimeout(() => { window.location.href = `/obras/${response.id}`; }, 1000);
      } else {
        setFormData({ titulo: '', anio: new Date().getFullYear().toString(), dimensiones: '', precio: '', notas: '' });
        setTecnicaInput('');
        setImagen(null);
      }
    } catch (err: any) {
      // El interceptor ya redirige a /login si es 401/403, pero si es otro error (ej: 422), lo mostramos
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredTecnicas = tecnicaInput.trim()
    ? tecnicas.filter((t) => t.nombre.toLowerCase().includes(tecnicaInput.toLowerCase()))
    : tecnicas;

  const inputClass = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-accent focus:border-accent outline-none transition';
  const labelClass = 'block text-sm font-medium text-text-secondary mb-2';

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
      <h2 className="font-serif text-3xl font-bold text-text-primary mb-8">
        {isEditMode ? 'Editar Obra' : 'Registrar Nueva Obra'}
      </h2>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 text-green-700 rounded-lg border border-green-200 text-sm" role="status">
          {isEditMode ? '✓ Obra actualizada. Redirigiendo...' : '✓ Obra creada exitosamente.'}
          {!isEditMode && <a href="/" className="underline font-semibold ml-2">Volver al catálogo</a>}
        </div>
      )}

      <div className="space-y-6">
        <div>
          <label htmlFor="titulo" className={labelClass}>Título *</label>
          <input id="titulo" name="titulo" type="text" required value={formData.titulo} onChange={handleChange} className={inputClass} placeholder="Nombre de la obra" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="anio" className={labelClass}>Año *</label>
            <input id="anio" name="anio" type="number" required value={formData.anio} onChange={handleChange} className={inputClass} />
          </div>
          <div>
            <label htmlFor="dimensiones" className={labelClass}>Dimensiones *</label>
            <input id="dimensiones" name="dimensiones" type="text" required value={formData.dimensiones} onChange={handleChange} className={inputClass} placeholder="100×80 cm" />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="precio" className={labelClass}>Precio (ARS)</label>
            <input id="precio" name="precio" type="number" value={formData.precio} onChange={handleChange} className={inputClass} placeholder="Opcional" />
          </div>

          <div className="relative">
            <label htmlFor="tecnica" className={labelClass}>Técnica *</label>
            <input
              id="tecnica" name="tecnica" type="text" required
              value={tecnicaInput}
              onChange={(e) => { setTecnicaInput(e.target.value); setShowSuggestions(true); }}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
              className={inputClass}
              placeholder="Escribe o elige una técnica"
              autoComplete="off"
            />

            {showSuggestions && filteredTecnicas.length > 0 && (
              <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-auto">
                {filteredTecnicas.map((t) => (
                  <li key={t.id}>
                    <button type="button" onMouseDown={(e) => e.preventDefault()}
                      onClick={() => { setTecnicaInput(t.nombre); setShowSuggestions(false); }}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 transition">
                      {t.nombre}
                    </button>
                  </li>
                ))}
              </ul>
            )}

            {showSuggestions && tecnicaInput.trim() && filteredTecnicas.length === 0 && (
              <div className="absolute z-10 w-full mt-1 bg-gray-50 border border-gray-200 rounded-lg shadow-lg px-4 py-2 text-sm text-text-secondary">
                Se creará la técnica "{tecnicaInput}" al guardar
              </div>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="imagen" className={labelClass}>Fotografía</label>

          {isEditMode && initialData?.imagen_url && !imagen && (
            <div className="mb-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-xs text-text-secondary mb-2 uppercase tracking-wide font-semibold">Imagen actual:</p>
              <img
                src={`${API_URL}${initialData.imagen_url}`}
                alt="Imagen actual de la obra"
                className="w-40 h-40 object-cover rounded-lg border border-gray-200"
              />
              <p className="text-xs text-text-secondary mt-2">Subí una nueva imagen para reemplazarla</p>
            </div>
          )}

          <input id="imagen" name="imagen" type="file" accept="image/*" onChange={handleFileChange}
            className="w-full text-sm text-text-secondary file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-text-primary file:text-white hover:file:bg-accent file:transition file:cursor-pointer" />

          {imagen && (
            <p className="mt-2 text-sm text-green-700">
              {isEditMode ? '📎 Nueva imagen a subir: ' : '📎 '}{imagen.name} ({(imagen.size / 1024).toFixed(0)} KB)
            </p>
          )}
        </div>

        <div>
          <label htmlFor="notas" className={labelClass}>Notas</label>
          <textarea id="notas" name="notas" rows={3} value={formData.notas} onChange={handleChange}
            className={`${inputClass} resize-none`} placeholder="Opcional" />
        </div>
      </div>

      <div className="mt-8 flex items-center gap-4">
        <button type="submit" disabled={loading}
          className="px-6 py-3 bg-text-primary text-white font-medium rounded-lg hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2">
          {loading ? '⏳ Guardando...' : isEditMode ? '💾 Guardar Cambios' : '💾 Guardar Obra'}
        </button>
        <a href={isEditMode ? `/obras/${initialData?.id}` : '/'} className="text-sm text-text-secondary hover:text-text-primary transition">
          Cancelar
        </a>
      </div>
    </form>
  );
}