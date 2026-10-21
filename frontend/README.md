# 🎨 Art Manager Frontend

Frontend moderno y performante para Art Manager, construido con **Astro 7** (SSR por defecto)
e **islas de React** para interactividad. Diseñado para galerías de arte con foco en
UX profesional, SEO y accesibilidad.

## 🚀 Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Framework | Astro | 7.3+ |
| UI Islands | React | 18+ |
| Styling | Tailwind CSS | 4.0 |
| Tipografía | Playfair Display + Inter | Google Fonts |
| Charts | Chart.js + react-chartjs-2 | — |
| Package Manager | pnpm | 9+ |
| Iconos | Lucide React | — |

## ✨ Características Principales

### Arquitectura
- 🏝️ **Island Architecture**: SSR por defecto, React solo donde se necesita interactividad
- 🚀 **Performance**: 0 JS en páginas estáticas, hidratación selectiva
- 🎨 **Design System**: Tailwind con paleta custom (text-primary, accent, bg-primary)
- 📱 **Mobile-first**: Responsive design en todas las páginas

### Páginas
| Ruta | Acceso | Descripción |
|---|---|---|
| `/` | Público | Landing page con SEO optimizado |
| `/catalogo` | Público | Catálogo velado (blur sobre imágenes, sin precios) |
| `/inventario` | 🔒 Privado | Catálogo completo con filtros avanzados |
| `/login` | Público | Formulario de autenticación |
| `/dashboard` | 🔒 Privado | Métricas y KPIs con Chart.js |
| `/crear` | 🔒 Privado | Formulario de nueva obra |
| `/obras/[id]` | 🔒 Privado | Detalle de obra |
| `/obras/[id]/editar` | 🔒 Privado | Edición de obra |
| `/tecnicas` | 🔒 Privado | Gestión de técnicas |

### Autenticación (Fase 2)
- 🔐 **Login con JWT** (access + refresh tokens en localStorage)
- 🔐 **Interceptor HTTP** automático (adjunta Bearer token)
- 🔐 **Route Guards** (redirige a `/login` si no hay token)
- 🔐 **UI condicional** (muestra/oculta botones según auth)
- 🔐 **Logout** con limpieza de tokens

### UX/UI
- ✅ Formularios con validación client-side
- ✅ Autocomplete inteligente de técnicas (crea on-the-fly)
- ✅ Subida de imágenes con preview
- ✅ Modales de confirmación para acciones destructivas
- ✅ Mensajes de éxito/error con toasts
- ✅ Estados de carga (loading spinners)

## 📂 Estructura del Proyecto

```bash
frontend/
├── src/
│ ├── components/
│ │ ├── ArtworkForm.tsx # Formulario reutilizable (crear/editar)
│ │ ├── ArtworkCardPublic.astro # Tarjeta de catálogo velado
│ │ ├── HeaderNav.tsx # Navegación condicional (isla React)
│ │ ├── RouteGuard.tsx # Protección de rutas privadas
│ │ ├── DashboardCharts.tsx # Gráficos Chart.js
│ │ ├── InventarioClient.tsx # Catálogo privado con filtros
│ │ └── DeleteArtworkButton.tsx # Botón con modal de confirmación
│ ├── layouts/
│ │ └── Layout.astro # Layout global con header + footer
│ ├── pages/
│ │ ├── index.astro # Landing page
│ │ ├── catalogo.astro # Catálogo público
│ │ ├── inventario.astro # Catálogo privado
│ │ ├── login.astro # Login
│ │ ├── dashboard.astro # Dashboard
│ │ ├── crear.astro # Nueva obra
│ │ ├── tecnicas/index.astro # Gestión de técnicas
│ │ └── obras/
│ │ ├── [id].astro # Detalle de obra
│ │ └── [id]/editar.astro # Edición
│ ├── services/
│ │ ├── auth.ts # Login/logout/tokens
│ │ ├── httpClient.ts # Interceptor HTTP (Bearer automático)
│ │ ├── api.ts # Endpoints privados (con auth)
│ │ └── publicApi.ts # Endpoints públicos (sin auth)
│ └── styles/
│ └── global.css # Tailwind + custom styles
├── public/
│ └── favicon.svg
├── .env # Variables de entorno
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
├── package.json
├── Dockerfile
└── README.md
```
## 🛠️ Instalación y Ejecución

### Opción A: Desarrollo Local (sin Docker)

1. **Entrar al directorio:**
   ```bash
   cd frontend
   ```
2. **Instalar dependencias:**
   ```bash
   pnpm install
   ```
3. **Crear archivo `.env`:**
   ```bash
   cp .env.example .env
   ```
   *Editar el archivo configurando las siguientes variables:*
   ```env
   PUBLIC_API_URL=http://localhost:8000
   API_URL=http://localhost:8000
   ```
4. **Ejecutar servidor de desarrollo:**
   ```bash
   pnpm dev
   ```

> 🌐 **Acceso:** Abrí tu navegador e ingresá a [http://localhost:4321](http://localhost:4321)

---

### Opción B: Con Docker Compose (Recomendado)

* **Iniciar el contenedor** (desde la raíz del monorepo):
  ```bash
  docker compose up -d frontend
  ```
* **Ver los logs** en tiempo real:
  ```bash
  docker compose logs -f frontend
  ```
* **Reiniciar el servicio** si aplicaste cambios en los archivos:
  ```bash
  docker compose restart frontend
  ```

## 🔧 Variables de Entorno

Crear archivo `.env` en `frontend/`:

```env
1234567
```

> ⚠️ **Importante:** En Docker Compose, `API_URL` debe ser `http://backend:8000` (red interna).

---

## 📚 Comandos Disponibles

| Comando | Acción |
| :--- | :--- |
| `pnpm dev` | Servidor de desarrollo en `localhost:4321` |
| `pnpm build` | Build de producción en `./dist/` |
| `pnpm preview` | Preview del build localmente |
| `pnpm astro check` | Validación de tipos y sintaxis |
| `pnpm astro add` | Agregar integraciones (React, Tailwind, etc.) |

---

## 🎨 Design System

### Paleta de Colores

```css
--text-primary: #1a1a1a;      /* Texto principal */
--text-secondary: #6b7280;    /* Texto secundario */
--bg-primary: #ffffff;        /* Fondo principal */
--accent: #8b5cf6;            /* Color de acento (morado) */
```

### Tipografía
* **Playfair Display (serif):** Títulos, headings
* **Inter (sans-serif):** Cuerpo de texto, UI

### Componentes Reutilizables
* Botones con estados (hover, focus, disabled)
* Tarjetas de obra (pública velada vs privada completa)
* Formularios con validación accesible
* Modales de confirmación
* Toasts de notificación

## 🏝️ Arquitectura de Islas (Island Architecture)

### Concepto Principal
* Astro renderiza todo en el servidor (SSR) por defecto, enviando 0 JavaScript al navegador.
* Solo los componentes que necesitan interactividad se hidratan con React:

```astro
12345
```

### Directivas de hidratación
* **`client:load`:** Hidrata inmediatamente al cargar la página
* **`client:visible`:** Hidrata cuando el componente entra en viewport
* **`client:idle`:** Hidrata cuando el navegador está idle
* **`client:only="react"`:** Solo se ejecuta en el cliente (no SSR)

---

## 🔐 Autenticación y Seguridad

### Flujo de Login
1. Usuario ingresa credenciales en `/login`
2. Frontend llama a `POST /auth/login`
3. Backend devuelve `access_token` + `refresh_token`
4. Frontend guarda tokens en `localStorage`
5. Interceptor HTTP adjunta `Authorization: Bearer <token>` en cada request

### Protección de Rutas
* Componente `<RouteGuard>` en páginas privadas
* Si no hay token → redirige a `/login?returnTo=/ruta-original`
* Después del login → redirige de vuelta a la ruta original

### UI Condicional
* `<HeaderNav>` muestra/oculta botones según `isLoggedIn`
* Botones de crear/editar/eliminar solo visibles para usuarios autenticados

---

## 🚢 Producción

### Pasos para deploy en producción
* **Build estático:** `pnpm build` genera archivos optimizados en `./dist/`
* **CDN:** Servir assets estáticos desde Cloudflare/AWS CloudFront
* **Variables de entorno:** Configurar `PUBLIC_API_URL` y `API_URL` según entorno
* **HTTPS obligatorio:** Todos los requests deben ser seguros
* **CSP Headers:** Configurar *Content Security Policy*
* **Seguridad de tokens:** Migrar tokens a cookies `httpOnly` para protección contra XSS

---

## 🗺️ Roadmap

### Estado del proyecto
* **✅ Fase 1:** CRUD completo + dashboard + filtros
* **✅ Fase 2:** Auth + UI condicional + route guards + catálogo velado
* **🟠 Fase 3 (próximo):** Multi-tenancy (URLs semánticas `/galeria-sur/artistas`)
* **🔵 Fase 4:** Features de dominio (certificados PDF, *provenance*)
* **🟣 Fase 5:** IA aplicada (clasificación automática de imágenes)

---

## 📚 Recursos

### Enlaces útiles
* Astro Docs
* Tailwind CSS
* React Docs
* Chart.js

---

## 📄 Licencia

**Privado** — Destinado únicamente para uso interno y el desarrollo del producto SaaS.

* **Contacto:** [email@dominio.com](matiaszelarayandev@gmail.com)
* **Repositorio:** [://github.com](https://github.com/R-Mutt22)