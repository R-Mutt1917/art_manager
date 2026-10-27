# ART MANAGER — Documento Maestro de Proyecto y Roadmap

> **Propósito de este documento:** Ser la fuente única de verdad del proyecto.  
> Cualquier developer o IA que continúe el trabajo DEBE leer esto primero.  
> **Regla de oro:** Al cerrar cada fase o hito, actualizar este documento (sección Changelog).

**Fecha de última actualización:** 27 de octubre de 2026  
**Estado actual:** ✅ **Fase 3 COMPLETA** (Multi-tenancy, SSR Auth, URLs Semánticas). Próximo: Fase 4 (Refactor de Roles + Features de Dominio).

## 1\. VISIÓN DEL PRODUCTO

**Art Manager** es una **plataforma SaaS multi-tenant** de gestión integral para galerías de arte latinoamericanas, artistas visuales y curadores independientes.

**Propuesta de valor diferenciada:**

> "Cada galería tiene su propia plataforma aislada con URLs semánticas (`/galeria-sur`, `/galeria-sur/artistas/julio-le-parc`), su catálogo, artistas y equipo, manteniendo datos completamente segregados. Todo con trazabilidad profesional, statement curatorial público y, a futuro, IA aplicada al mercado del arte."

**Usuarios objetivo:**

-   Galerías medianas a grandes (Buenos Aires, CDMX, Bogotá, Santiago)
-   Curadores independientes gestionando múltiples artistas
-   Artistas consagrados con inventarios extensos
-   Coleccionistas serios con portfolios

## 2\. STACK TÉCNICO

| Capa     | Tecnología                                                   | Notas                                                       |
| -------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| Backend  | FastAPI + SQLModel + SQLite (→ PostgreSQL en Fase 4)         | Arquitectura en capas, aislamiento por galeria_id           |
| Frontend | Astro 7 (SSR output: 'server') + React islands + Tailwind v4 | Islas React solo donde se necesita interactividad           |
| Auth     | PyJWT + bcrypt + Cookies SSR (artmanager_token)              | Access tokens en cookie para SSR, localStorage para cliente |
| Infra    | Docker Compose                                               | Hot reload real en ambos servicios                          |
| Testing  | pytest (~67 passing) + Playwright (E2E setup)                | Tests unitarios backend + E2E frontend                      |
| Gestores | pnpm (front) / pip + venv (back, solo para tests locales)    |                                                             |

### Estructura del monorepo

```
art_manager/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py              # lifespan: crea tablas + seeds (incluye dev users)
│   │   ├── database.py          # engine, get_session
│   │   ├── seed.py              # Técnicas, admin, Galería Demo, Artista Demo, Dev Users
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings + JWT config
│   │   │   ├── security.py      # bcrypt + PyJWT
│   │   │   └── dependencies.py  # get_current_user, require_role, get_current_galeria
│   │   ├── models/              # Galeria, Artista, Obra, Tecnica, Comprador, Exposicion, Prestamo, Usuario, AuditLog
│   │   ├── schemas/             # Pydantic Create/Update/Read + PublicRead (velados)
│   │   ├── services/            # Lógica de negocio filtrada por galeria_id
│   │   └── routers/             # obras, tecnicas, compradores, exposiciones, prestamos, dashboard, auth, audit, galerias
│   └── tests/                   # ~67 tests passing
└── frontend/
    ├── playwright/              # Setup E2E (config, e2e specs)
    └── src/
        ├── pages/               # Landing, galerias/[slug], obras/[id]/index.astro, etc.
        ├── components/          # ArtworkForm, ArtworkCardPublic, HeaderNav, RouteGuard, etc.
        ├── layouts/Layout.astro # Layout global con HeaderNav (isla React)
        └── services/            # api.ts, auth.ts (cookie + localStorage), httpClient.ts, apiPublic.ts
```
### Variables de entorno (CRÍTICO)

-   `PUBLIC_API_URL=http://localhost:8000` → código del **navegador** (React, `<img src>`, `<a href>`).
-   `API_URL=http://backend:8000` → código del **servidor** (Astro SSR frontmatter, red interna Docker).
-   `SECRET_KEY` → clave para firmar JWTs (32+ chars en producción).
-   Definidas en `docker-compose.yml` y `frontend/.env`.

## 3\. ESTADO ACTUAL — LO QUE FUNCIONA ✅

### Backend

-   ✅ **Multi-tenancy total**: Modelos `Galeria` y `Artista`. Todas las entidades (`Obra`, `Comprador`, `Prestamo`, `Exposicion`, `Usuario`) tienen `galeria_id` y están aisladas por middleware.
-   ✅ **Seed inteligente**: Crea Galería Demo, Artista Demo, migra datos legacy y crea 4 usuarios demo por rol (`dueno`, `curador`, `asesor`, `viewer` con pass `demo1234`).
-   ✅ **SSR Auth**: Endpoints privados validan cookie `artmanager_token`.
-   ✅ **Catálogo público semántico**: `/galerias/{slug}`, `/galerias/{slug}/artistas`, `/galerias/{slug}/artistas/{artistaSlug}`.
-   ✅ **Campo `**statement**`**: Texto curatorial público en obras, separado de `notas` privadas.
-   ✅ **~67 tests passing**: Cobertura completa de aislamiento multi-tenant y CRUD.

### Frontend

-   ✅ **Landing page estilo Artsy**: SSR fetch de obras destacadas, tipografía elegante, doble CTA (B2C/B2B).
-   ✅ **Rutas públicas funcionales**: Perfiles de galería y artistas con imágenes cargando correctamente (usando `PUBLIC_API_URL`).
-   ✅ **SSR Auth real**: `obras/[id]/index.astro` y `editar.astro` leen la cookie en el frontmatter y hacen `Astro.redirect('/login')` si no hay token, evitando flashes de contenido no autorizado.
-   ✅ **Playwright E2E**: Configurado con `@playwright/test`, `@types/node`, y scripts `test:e2e`, `test:e2e:ui`.

## 4\. CONTRATO REAL DE LA API (referencia rápida)

### Rutas Públicas Semánticas (Sin Auth)

| Método | Ruta                                     | Notas                                          |
| ------ | ---------------------------------------- | ---------------------------------------------- |
| GET    | /galerias/{slug}                         | Perfil de galería + contadores                 |
| GET    | /galerias/{slug}/artistas                | Listado de artistas activos                    |
| GET    | /galerias/{slug}/artistas/{artista_slug} | Perfil artista + obras veladas (con statement) |

### Auth & Multi-tenancy

-   Todos los endpoints de escritura (`POST`, `PUT`, `DELETE`) en `/obras/`, `/compradores/`, etc., requieren `Authorization: Bearer <token>` Y que el recurso pertenezca a la `galeria_id` del usuario.
-   `GET /dashboard/stats`: Filtra métricas agregadas estrictamente por `galeria_id`.

## 5\. LECCIONES APRENDIDAS / TRAMPAS CONOCIDAS 🕳️ (ACTUALIZADO)

### Arquitectura & Docker

1.  **Dos URLs, dos consumidores**:
2.  -   `API_URL` (`http://backend:8000`) → **SOLO** para `fetch()` en el frontmatter de Astro (server-to-server en red Docker).
    -   `PUBLIC_API_URL` (`http://localhost:8000`) → Para **TODO** lo que renderiza el navegador (`<img src>`, `<a href>`, meta tags). Mezclarlas causa imágenes rotas o fetches fallidos.
3.  **Astro SSR + localStorage**: `localStorage` no existe en el servidor. Para proteger páginas con SSR, leer el token de la cookie (`Astro.cookies.get('artmanager_token')`) y usar `Astro.redirect('/login')` en el frontmatter. No confiar en `RouteGuard` de React para evitar que el HTML sensible se genere.
4.  **Ritual de reinicio de Astro en Docker**: `docker compose restart` a menudo deja procesos zombie y no limpia la cache de rutas. El reset correcto es: `docker compose down` → `Remove-Item frontend\.astro, frontend\node_modules\.vite` → `docker compose up -d`.
5.  **NUNCA montar un volumen nombrado sobre `**/app**`**: tapa el código del bind mount y rompe el hot reload.

### PowerShell & Windows

5.  **PowerShell + corchetes = wildcard**: Comandos como `Test-Path`, `Move-Item`, `Select-String` interpretan `[slug]` como un patrón de caracteres. **Solución**: Usar el flag `-LiteralPath` o métodos de .NET: `[System.IO.File]::Move("$PWD\src\pages\galerias\[slug].astro", "$PWD\src\pages\galerias\[slug]\index.astro")`.
6.  **Docker bind mount + Windows**: Las operaciones de move/write de .NET desde PowerShell a veces no se propagan bien al contenedor Linux (archivos de 0 bytes o no vistos). **Solución**: Abrir el archivo en VS Code y guardar (`Ctrl+S`), o usar `printf`/`cat` directamente dentro del contenedor (`docker compose exec frontend sh -c "..."`).

### FastAPI & Testing

7.  **Orden de paths**: Paths estáticos (`/publicas`) SIEMPRE antes que dinámicos (`/{id}`), sino FastAPI interpreta el texto como parámetro.
8.  **Playwright en monorepo**: Instalar `@playwright/test` y `@types/node` como dev dependencies en el frontend. Configurar `playwright.config.ts` con `fullyParallel: false` y `workers: 1` para evitar conflictos de base de datos entre tests simultáneos.

## 6\. ROADMAP POR FASES

### ✅ FASE 1 — CRUD Completo y Pulido (COMPLETA)

### ✅ FASE 2 — Autenticación, Roles y Auditoría (COMPLETA)

### ✅ FASE 3 — Multi-tenancy y Plataforma SaaS (COMPLETA)

-   3.1 Modelos `Galeria` y `Artista` + FK `galeria_id` en todas las entidades.
-   3.2 Aislamiento de datos: Middleware `get_current_galeria()` y filtros en todos los services.
-   3.3 URLs semánticas públicas: `/galerias/{slug}`, `/artistas`, etc.
-   3.4 Campo `statement` curatorial público en obras.
-   3.5 Landing page pública estilo Artsy con SSR fetch.
-   3.6 Auth SSR robusto: Cookies + `Astro.redirect` en frontmatter.
-   3.7 Setup de Playwright E2E.

### 🔵 FASE 4 — Refactor de Roles y Features de Dominio (SIGUIENTE PRIORIDAD)

**Objetivo:** Resolver la deuda arquitectónica de roles y agregar valor de dominio.

#### 4.1 Refactor de Jerarquía de Roles (CRÍTICO)

-   **Problema actual**: `ADMIN` actúa como super-usuario global. Un curador que trabaja en 2 galerías necesita 2 emails distintos.
-   **Solución**:
-   -   Crear modelo `UserAccount` (identidad global: email, password).
    -   Crear modelo `UserGalleryRole` (tabla intermedia: `user_id`, `galeria_id`, `rol`).
    -   Flujo: Super Admin crea la plataforma → Dueño de Galería se registra → Dueño invita a Curadores/Asesores a SU galería específica.
    -   Un usuario (`juan@ejemplo.com`) puede ser `ADMIN` en Galería A y `CURADOR` en Galería B.

#### 4.2 Rol ARTISTA (Diferenciador)

-   Acceso limitado para que el artista vea SUS obras, edite su bio/statement y proponga nuevas obras (estado "pendiente" para aprobación del curador).

#### 4.3 Features de Dominio

-   Certificados de autenticidad en PDF con QR.
-   Provenance (timeline de la obra).
-   Exportar inventario a PDF/Excel (reportes para ferias).
-   Búsqueda y filtros avanzados en el catálogo público.

## 7\. PRÓXIMAS TAREAS INMEDIATAS

-   **T8-2**: Escribir los primeros tests E2E con Playwright (`01-auth.spec.ts`, `02-roles.spec.ts`).
-   **T8-3**: Documentar formalmente la deuda de roles en el backlog de Fase 4.
-   **T9**: Iniciar refactor de `UserAccount` + `UserGalleryRole` (requiere migración de datos y actualización de `dependencies.py`).

## 8. CHEATSHEET DE COMANDOS

```powershell
# Levantar todo
docker compose up -d
docker compose logs -f

# Reset nuclear controlado (CUANDO ASTRO NO DETECTA RUTAS O HAY ZOMBIES)
docker compose down
Remove-Item -Recurse -Force frontend\.astro -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force frontend\node_modules\.vite -ErrorAction SilentlyContinue
docker compose up -d

# Mover archivos con corchetes de forma segura en Windows
[System.IO.File]::Move("$PWD\src\pages\galerias\[slug].astro", "$PWD\src\pages\galerias\[slug]\index.astro")

# Tests backend
cd backend; .\venv\Scripts\activate; pytest tests/ -v
del test_database.db 2>$null   # Reset BD de tests

# Tests E2E Frontend
cd frontend
pnpm test:e2e          # Correr todos los tests E2E en terminal
pnpm test:e2e:ui       # Abrir interfaz gráfica de Playwright
pnpm test:e2e:debug    # Modo debug paso a paso

# Git
git add .
git commit -m "tipo(ámbito): descripción" -m "Detalle opcional"
git push origin develop
```
---

## 9\. DECISIONES PENDIENTES

-   **Arquitectura de Roles**: Aprobar el cambio a `UserAccount` + `UserGalleryRole` (Prioridad Alta).
-   **Migración a PostgreSQL**: Planificar el uso de Alembic antes de que la BD de SQLite crezca demasiado con datos de prueba.
-   **Deploy**: Definir si se usa Railway, Fly.io o VPS propio para la demo pública.
-   **CDN de imágenes**: Evaluar Cloudflare R2 o AWS S3 para las imágenes subidas en Fase 4.

## 10\. CHANGELOG DE HITOS

### Día X — Cierre de Fase 3: Multi-tenancy, SSR Auth, URLs Semánticas y Playwright

-   **Backend**: Modelos `Galeria` y `Artista`. Refactor de `Obra`, `Comprador`, `Prestamo`, `Exposicion` con `galeria_id`.
-   **Backend**: Aislamiento total en Services y Routers. Seed de usuarios demo por rol (`demo1234`).
-   **Backend**: Campo `statement` (público) añadido a `Obra`, separado de `notas` (privado).
-   **Backend**: ~67 tests passing validando el aislamiento multi-tenant.
-   **Frontend**: Rutas públicas semánticas (`/galerias/{slug}`, etc.) con `apiPublic.ts` (fetch server-side).
-   **Frontend**: Landing page estilo Artsy con fetch SSR de obras destacadas.
-   **Frontend**: Auth SSR robusto: `obras/[id]` y `editar` leen cookie `artmanager_token` y redirigen con `Astro.redirect` si no hay sesión.
-   **Frontend**: Fix crítico de imágenes: separación estricta de `API_URL` (server) y `PUBLIC_API_URL` (browser).
-   **Frontend**: Setup completo de Playwright E2E con `@types/node` y configuración secuencial.
-   **Arquitectura**: Identificada y documentada la deuda crítica de jerarquía de roles (`UserAccount` vs `UserGalleryRole`).

### Día 4 — Cierre de Fase 2: Auth completo + Auditoría + Route Guards

-   *(Histórico: Ver versiones anteriores del documento)*

*Fin del documento. Actualizar al cerrar cada fase.*