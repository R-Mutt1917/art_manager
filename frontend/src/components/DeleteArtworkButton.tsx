import { useState } from 'react';

interface DeleteArtworkButtonProps {
  obraId: number;
  obraTitulo: string;
}

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export default function DeleteArtworkButton({ obraId, obraTitulo }: DeleteArtworkButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/obras/${obraId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || 'No se pudo eliminar la obra');
      }

      // Éxito: redirigir al catálogo
      window.location.href = '/';
    } catch (err: any) {
      setError(err.message || 'Error al eliminar');
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-2 text-sm font-medium px-3 py-1.5 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
        </svg>
        Eliminar
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-2xl border border-gray-100">
            <h3 className="font-serif text-xl font-bold text-text-primary mb-2">¿Dar de baja esta obra?</h3>
            <p className="text-text-secondary mb-6 text-sm leading-relaxed">
              Estás a punto de marcar <strong>"{obraTitulo}"</strong> como inactiva. 
              La obra no se borrará de la base de datos, pero dejará de ser visible en el catálogo público.
            </p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200" role="alert">
                {error}
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => { setIsOpen(false); setError(null); }}
                disabled={loading}
                className="px-4 py-2 text-text-secondary hover:text-text-primary font-medium transition disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={loading}
                className="px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2"
              >
                {loading ? '⏳ Procesando...' : 'Sí, dar de baja'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}