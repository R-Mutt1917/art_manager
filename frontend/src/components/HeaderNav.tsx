// frontend/src/components/HeaderNav.tsx
import { useState, useEffect } from 'react';
import { estaAutenticado, logout } from '../services/auth';

export default function HeaderNav() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Al montar el componente, verificamos si hay token
  useEffect(() => {
    setIsLoggedIn(estaAutenticado());
  }, []);

  // Función para cerrar sesión
  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
  };

  return (
    <nav aria-label="Navegación principal" className="flex items-center gap-6">
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
      <div className="flex items-center gap-3">
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