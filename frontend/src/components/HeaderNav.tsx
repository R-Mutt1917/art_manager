import { useState, useEffect } from 'react';

const ACCESS_TOKEN_KEY = 'artmanager_access_token';
const REFRESH_TOKEN_KEY = 'artmanager_refresh_token';

// Función para decodificar el token JWT y obtener el payload
const getPayloadFromToken = (token: string) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

// Verificar permisos según el rol
const canCreateObra = (rol: string | null) => {
  return rol === 'admin' || rol === 'curador';
};

const canViewDashboard = (rol: string | null) => {
  return rol === 'admin' || rol === 'curador' || rol === 'asesor';
};

const canViewInventarioPrivado = (rol: string | null) => {
  return rol === 'admin' || rol === 'curador' || rol === 'asesor';
};

const checkAuth = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(ACCESS_TOKEN_KEY) !== null;
  }
  return false;
};

export default function HeaderNav() {
  const [isLoggedIn, setIsLoggedIn] = useState(checkAuth());
  const [userRol, setUserRol] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (token) {
        const payload = getPayloadFromToken(token);
        setUserRol(payload?.rol || null);
      }
      setIsLoggedIn(checkAuth());
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setIsLoggedIn(false);
    setUserRol(null);
    window.location.href = '/';
  };

  // Determinar a dónde va el link "Inventario/Catálogo" según el rol
  const catalogoLink = canViewInventarioPrivado(userRol) ? '/inventario' : '/catalogo';
  const catalogoLabel = canViewInventarioPrivado(userRol) ? 'Inventario' : 'Catálogo';

  return (
    <nav aria-label="Navegación principal" className="flex items-center gap-6 transition-all duration-300">
      <ul className="hidden md:flex gap-6 text-sm font-medium text-text-secondary">
        <li>
          <a href="/" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
            Inicio
          </a>
        </li>
        <li>
          <a href={catalogoLink} className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
            {catalogoLabel}
          </a>
        </li>
        
        {/* Solo ADMIN, CURADOR y ASESOR ven Dashboard */}
        {isLoggedIn && canViewDashboard(userRol) && (
          <li>
            <a href="/dashboard" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
              Dashboard
            </a>
          </li>
        )}
        
        {/* Solo ADMIN y CURADOR ven Técnicas */}
        {isLoggedIn && (userRol === 'admin' || userRol === 'curador') && (
          <li>
            <a href="/tecnicas" className="hover:text-text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1">
              Técnicas
            </a>
          </li>
        )}
      </ul>

      <div className="flex items-center gap-3 transition-all duration-300">
        {isLoggedIn ? (
          <>
            {/* Solo ADMIN y CURADOR ven el botón "+ Nueva Obra" */}
            {canCreateObra(userRol) && (
              <a 
                href="/crear" 
                className="px-4 py-2 bg-text-primary text-white text-sm font-semibold rounded-lg hover:bg-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
              >
                + Nueva Obra
              </a>
            )}
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