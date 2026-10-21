import { useState, useEffect } from 'react';

const ACCESS_TOKEN_KEY = 'artmanager_access_token';
const REFRESH_TOKEN_KEY = 'artmanager_refresh_token';

// Función segura: lee el token solo si estamos en el navegador
const checkAuth = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(ACCESS_TOKEN_KEY) !== null;
  }
  return false;
};

export default function HeaderNav() {
  // Inicializamos el estado leyendo directamente (elimina el retraso del useEffect)
  const [isLoggedIn, setIsLoggedIn] = useState(checkAuth());

  useEffect(() => {
    // Doble verificación por si el estado cambió entre el render inicial y la hidratación
    setIsLoggedIn(checkAuth());
  }, []);

  const handleLogout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setIsLoggedIn(false);
    window.location.href = '/';
  };

  return (
    // Agregamos transition-all para que cualquier cambio de tamaño sea suave
    <nav aria-label="Navegación principal" className="flex items-center gap-6 transition-all duration-300">
      <ul className="hidden md:flex gap-6 text-sm font-medium text-text-secondary">
        <li>
          <a href="/" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
            Inicio
          </a>
        </li>
        <li>
          <a href="/catalogo" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
            Catálogo
          </a>
        </li>
        
        {/* Links SOLO para usuarios logueados */}
        {isLoggedIn && (
          <>
            <li>
              <a href="/dashboard" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
                Dashboard
              </a>
            </li>
            <li>
              <a href="/tecnicas" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
                Técnicas
              </a>
            </li>
          </>
        )}
      </ul>

      {/* Botones de Acción */}
      <div className="flex items-center gap-3 transition-all duration-300">
        {isLoggedIn ? (
          <>
            <a 
              href="/crear" 
              className="px-4 py-2 bg-text-primary text-white text-sm font-semibold rounded-lg hover:bg-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
            >
              + Nueva Obra
            </a>
            <button 
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-red-600 transition-colors"
            >
              Salir
            </button>
          </>
        ) : (
          <a 
            href="/login" 
            className="px-4 py-2 bg-accent text-white text-sm font-semibold rounded-lg hover:bg-accent/90 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            Iniciar Sesión
          </a>
        )}
      </div>
    </nav>
  );
}