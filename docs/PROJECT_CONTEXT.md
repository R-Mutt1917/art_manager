# ART MANAGER — Documento Maestro de Proyecto y Roadmap

> **Propósito de este documento:** Ser la fuente única de verdad del proyecto.
> Cualquier developer o IA que continúe el trabajo DEBE leer esto primero.
> **Regla de oro:** Al cerrar cada fase o hito, actualizar este documento (sección Changelog).

**Fecha de última actualización:** 21 de octubre de 2026  
**Estado actual:** Fase 2 COMPLETA (Autenticación + Roles + Auditoría). Próximo: Fase 3 (Multi-tenancy SaaS).

---

## 1. VISIÓN DEL PRODUCTO

**Art Manager** es una **plataforma SaaS** de gestión integral para galerías de arte latinoamericanas, artistas visuales y curadores independientes.

**Propuesta de valor diferenciada:**
> "Cada galería tiene su propia plataforma aislada (multi-tenant) con URLs semánticas (`/galeria-sur`, `/ruth-benzacar`), su catálogo, artistas y equipo, manteniendo datos completamente segregados. Todo con trazabilidad profesional y, a futuro, IA aplicada al mercado del arte."

**Usuarios objetivo:**
- Galerías medianas a grandes (Buenos Aires, CDMX, Bogotá, Santiago)
- Curadores independientes gestionando múltiples artistas
- Artistas consagrados con inventarios extensos
- Coleccionistas serios con portfolios

---

## 2. STACK TÉCNICO

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Backend | FastAPI + SQLModel + SQLite (→ PostgreSQL en Fase 3) | Arquitectura en capas |
| Frontend | Astro 7 (SSR) + React islands + Tailwind CSS v4 | Islas React solo donde se necesita interactividad |
| Auth | PyJWT + bcrypt | Access + refresh tokens |
| Infra | Docker Compose | Hot reload real en ambos servicios |
| Testing | pytest + fastapi.TestClient | **~33 tests passing** |
| Gestores | pnpm (front) / pip + venv (back, solo para tests locales) | |

### Estructura del monorepo
```
art_manager/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py              # lifespan: crea tablas + seeds
│   │   ├── database.py          # engine, get_session
│   │   ├── seed.py              # 7 técnicas + admin user
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings + JWT config
│   │   │   ├── security.py      # bcrypt + PyJWT
│   │   │   └── dependencies.py  # get_current_user + require_role
│   │   ├── models/              # Obra, Tecnica, Comprador, Exposicion, Prestamo, Usuario, AuditLog
│   │   ├── schemas/             # Pydantic Create/Update/Read por entidad
│   │   ├── services/            # Lógica de negocio + AuditService
│   │   └── routers/             # obras, tecnicas, compradores, exposiciones, prestamos, dashboard, auth, audit
│   └── tests/                   # ~34 tests
└── frontend/
    └── src/
        ├── pages/               # Landing, catálogo, inventario, login, dashboard, etc.
        ├── components/          # ArtworkForm, ArtworkCardPublic, HeaderNav, RouteGuard, etc.
        ├── layouts/Layout.astro # Layout global con HeaderNav (isla React)
        └── services/            # api.ts, auth.ts, httpClient.ts, publicApi.ts
```

### Variables de entorno (CRÍTICO)
- `PUBLIC_API_URL=http://localhost:8000` → código del **navegador** (React).
- `API_URL=http://backend:8000` → código del **servidor** (Astro SSR, red interna Docker).
- `SECRET_KEY` → clave para firmar JWTs (32+ chars en producción).
- Definidas en `docker-compose.yml` y `frontend/.env`.

---

## 3. ESTADO ACTUAL — LO QUE FUNCIONA ✅

### Backend
- ✅ **CRUD de obras** con subida de imagen y upsert de técnica por nombre.
- ✅ **PUT de obras** con FormData (reemplaza imagen en la misma operación).
- ✅ **Soft delete** de obras y compradores.
- ✅ **CRUD completo de técnicas** con validación de obras asociadas.
- ✅ **Ventas** que cambian estado de obra a `vendida`.
- ✅ **Exposiciones** con validación de superposición de fechas + checklist.
- ✅ **Préstamos** con ciclo completo y validación de obra vendida.
- ✅ **Filtros avanzados** en GET /obras/ (estado, técnica, precio, búsqueda).
- ✅ **Dashboard** con métricas agregadas y top técnicas.
- ✅ **Autenticación JWT**: register, login, refresh (Fase 2).
- ✅ **Autorización por roles**: ADMIN/CURADOR/ASESOR/ARTISTA/VIEWER.
- ✅ **Catálogo público velado**: GET /obras/publicas sin datos sensibles.
- ✅ **Auditoría**: tabla audit_logs con eventos de auth (Fase 2.9).
- ✅ **CORS** habilitado + servido de imágenes en /uploads.

### Frontend
- ✅ **Landing page** con SEO en `/`.
- ✅ **Catálogo público velado** en `/catalogo` (blur CSS sobre imágenes, sin precios).
- ✅ **Catálogo privado** en `/inventario` (precios, HD, filtros) - protegido por RouteGuard.
- ✅ **Login** en `/login` con tokens en localStorage.
- ✅ **Interceptor HTTP** que adjunta Bearer automáticamente (SSR-safe).
- ✅ **HeaderNav** como isla de React: muestra UI adaptativa según auth.
- ✅ **RouteGuard** que protege páginas privadas.
- ✅ **Dashboard** con KPIs y Chart.js (usa httpClient).
- ✅ **Formulario reutilizable** ArtworkForm.tsx (crear/editar).

### Tests: ~33 PASSED
- test_auth.py (8): register, login, refresh, seed admin.
- test_obras.py (11): CRUD + filtros + autorización.
- test_tecnicas.py (4): CRUD + autorización.
- test_compradores.py (2): ventas.
- test_exposiciones.py (3): asignación + checklist.
- test_prestamos.py (2): ciclo completo.
- test_audit.py (3): logs de login y permisos.

---

## 4. CONTRATO REAL DE LA API (referencia rápida)

### Auth (público)
| Método | Ruta | Body | Notas |
|--------|------|------|-------|
| POST | `/auth/register` | JSON UsuarioCreate | Rol siempre VIEWER |
| POST | `/auth/login` | JSON LoginRequest | Devuelve access + refresh tokens |
| POST | `/auth/refresh` | JSON RefreshRequest | Renueva par de tokens |

### Obras
| Método | Ruta | Auth | Notas |
|--------|------|------|-------|
| POST | `/obras/` | ADMIN, CURADOR | FormData |
| GET | `/obras/` | Público | Con filtros |
| GET | `/obras/publicas` | Público | Sin datos sensibles |
| GET | `/obras/{id}` | Público | 404 si inactiva |
| PUT | `/obras/{id}` | ADMIN, CURADOR | FormData |
| DELETE | `/obras/{id}` | ADMIN, CURADOR | Soft delete |
| POST | `/obras/{id}/imagen` | ADMIN, CURADOR | file |
| DELETE | `/obras/{id}/imagen` | ADMIN, CURADOR | |

### Técnicas (CRUD protegido, GETs públicos)
- POST/PUT/DELETE requieren ADMIN o CURADOR
- DELETE falla con 400 si tiene obras asociadas

### Compradores
- POST/PUT: ADMIN, ASESOR
- DELETE: solo ADMIN
- POST /compradores/ventas/registrar: ADMIN, ASESOR
- GETs: públicos

### Exposiciones (ADMIN, CURADOR para escribir)
### Préstamos (solo ADMIN para escribir)
### Dashboard (GET /dashboard/stats: ADMIN, CURADOR, ASESOR)
### Auditoría (GET /audit/logs: solo ADMIN)

### Estados de obra (enum EstadoObra)
`disponible` · `vendida` · `en_exposicion` · `en_prestamo`

### Roles de usuario (enum RolUsuario)
`admin` · `curador` · `asesor` · `artista` · `viewer`

---

## 5. LECCIONES APRENDIDAS / TRAMPAS CONOCIDAS 🕳️

### Arquitectura & Docker
1. **NUNCA montar un volumen nombrado sobre `/app`**: tapa el código del bind mount y rompe hot reload.
2. **Dos URLs de API**: `PUBLIC_API_URL` (cliente, `localhost:8000`) vs `API_URL` (servidor Docker, `backend:8000`). El `httpClient.ts` debe elegir según `typeof window === 'undefined'`.
3. **CORS**: el navegador bloquea fetch cross-origin; el SSR de Astro no. Por eso existen DOS variables.
4. **Reset nuclear controlado:** `docker compose down -v` borra BD y volúmenes.

### FastAPI
5. **Orden de paths**: paths estáticos (`/publicas`) SIEMPRE antes que dinámicos (`/{id}`), sino FastAPI interpreta el texto como parámetro.
6. **Enums en Python**: miembros con MAYÚSCULAS (`EstadoObra.DISPONIBLE`), `.value` para el string.
7. **Tests con FormData**: `data=` + `files=`, NO JSON.
8. **Bearer token sin header**: FastAPI HTTPBearer devuelve 403 (no 401) cuando falta el header.

### Astro + React
9. **SSR vs Cliente**: `localStorage` solo existe en el navegador. Usar `typeof window !== 'undefined'` para código isomórfico.
10. **Astro y rutas dinámicas**: crear carpetas nuevas (`[id]/`) con servidor corriendo a veces requiere `docker compose restart frontend`.
11. **React y SVG**: camelCase en JSX (`strokeWidth`), kebab-case en .astro (`stroke-width`).
12. **Flash of Unauthenticated Content**: evitar con `useState(checkAuth())` síncrono + `transition-all` CSS.
13. **Scripts con imports en Astro**: siempre `<script type="module">`.
14. **Arquitectura de Islas**: Astro envía 0 JS por defecto; `client:load` o `client:only="react"` hidrata donde se necesita interactividad.

### Seguridad
15. **Tokens en localStorage son MVP**: vulnerables a XSS. En producción migrar a cookies httpOnly.
16. **Interface Segregation (SOLID)**: interfaces separadas para datos públicos (`PublicObra`) vs privados (`Obra`).
17. **Blur CSS vs Server-side blur**: blur del cliente es vulnerable a DevTools; para producción usar thumbnails generados con Pillow.
18. **Register siempre crea VIEWER**: seguridad por defecto, evita que un atacante se registre como ADMIN pasando campos en JSON.

### Testing
19. **Test isolation**: cada test con su propia BD limpia (drop_all al final).
20. **Pylance warnings**: seleccionar el interpreter del venv en VS Code.
21. **Deuda técnica**: `datetime.utcnow()` deprecado (migrar a `datetime.now(datetime.UTC)`).

---

## 6. ROADMAP POR FASES

### ✅ FASE 1 — CRUD Completo y Pulido (COMPLETA)
- [x] F1.1 Editar obra: `/obras/[id]/editar` con form React prellenado.
- [x] F1.2 Eliminar obra con modal de confirmación.
- [x] F1.3 Reemplazar/eliminar imagen desde formulario de edición.
- [x] F1.4 CRUD de técnicas con validación de obras asociadas.
- [x] F1.5 Filtros avanzados en catálogo (query params + debounce).
- [x] F1.6 Dashboard con KPI cards + Chart.js.
- [x] F1.7 Navegación global en Layout.

### ✅ FASE 2 — Autenticación, Roles y Auditoría (COMPLETA)
- [x] 2.1 Modelo `Usuario` con roles (ADMIN/CURADOR/ASESOR/ARTISTA/VIEWER).
- [x] 2.2 Hash bcrypt + JWT (access + refresh).
- [x] 2.3 Endpoints `/auth/register`, `/login`, `/refresh`.
- [x] 2.4 Dependencias `get_current_user` + `require_role()`.
- [x] 2.5 Protección de endpoints por matriz de permisos.
- [x] 2.6 Catálogo público velado (`/obras/publicas`).
- [x] 2.7 Seed de usuario admin.
- [x] 2.8 Tests de auth y autorización.
- [x] 2.9 Auditoría (`audit_logs` + eventos de login/registro).

**Frontend Fase 2:**
- [x] F2F-1 Página `/login` estática.
- [x] F2F-2 Servicio `auth.ts` con localStorage.
- [x] F2F-3 Interceptor HTTP (Bearer automático + manejo 401/403).
- [x] F2F-4 Landing page con SEO.
- [x] F2F-5 Catálogo velado (blur + datos públicos).
- [x] F2F-6 UI condicional (HeaderNav como isla React).
- [x] F2F-7 Route Guards + `/inventario` (catálogo privado).

### 🟠 FASE 3 — Multi-tenancy y Plataforma SaaS (SIGUIENTE PRIORIDAD)

**Objetivo:** Convertir el sistema en plataforma para N galerías.

#### 3.1 Modelos de multi-tenancy
- Modelo `Galeria`: slug, nombre, logo, bio, ubicación, sitio_web, configuración.
- Modelo `Artista`: galeria_id, nombre, slug, bio, foto_perfil, cv_url.
- Refactor `Obra`: agregar `artista_id` + `galeria_id` (FKs).
- Refactor `Usuario`: agregar `galeria_id` (pertenencia).
- Migración: asignar datos existentes a "Galería Demo".

#### 3.2 Aislamiento de datos
- Middleware `get_current_galeria()` que filtra por `galeria_id`.
- Todas las queries incluyen `WHERE galeria_id = X`.
- Tests de aislamiento (Galería A no ve datos de Galería B).

#### 3.3 URLs semánticas (SEO)
```
Público:
  /                           → Landing plataforma
  /galerias                   → Directorio
  /galeria-sur                → Home galería
  /galeria-sur/artistas       → Listado artistas
  /galeria-sur/julio-le-parc  → Perfil artista + obras
  /galeria-sur/obras/42       → Detalle público velado

Privado:
  /app/inventario             → CRUD obras
  /app/artistas               → CRUD artistas
  /app/dashboard              → Métricas de la galería
```

#### 3.4 Onboarding de galerías
- Endpoint `POST /galerias/register` (self-service).
- Wizard: datos → admin user → primera obra.
- Subdominio opcional: `galeriasur.artmanager.com`.

#### 3.5 Migración SQLite → PostgreSQL
- Necesario para multi-tenancy robusto.
- Scripts de migración con Alembic.

#### 3.6 Planes de suscripción
- Modelo `Suscripcion`: plan (free/pro/enterprise), fecha_vencimiento.
- Límites por plan: obras máximas, usuarios, storage.

### 🔵 FASE 4 — Features de Dominio
- Certificados de autenticidad en PDF con QR.
- Provenance (timeline de la obra).
- Condition reports (fotos antes/después).
- Sistema de ofertas y negociación.
- Modo "Viewing Room" (Three.js).

### 🟣 FASE 5 — IA Aplicada al Arte
- Auto-clasificación de técnica/estilo (GPT-4 Vision / CLIP).
- Descripción curatorial automática.
- Valuación asistida por comparables (RAG).
- Detección de atribución.
- Recomendación obra ↔ exposición.

---

## 7. PRÓXIMAS TAREAS INMEDIATAS

### Cerrar Fase 2 (pendiente de esta sesión)
- [x] Commit final de Fase 2 + actualizar docs.

### Arrancar Fase 3 (siguiente sesión)
- [ ] Diseñar modelos `Galeria` y `Artista` (esquema de datos).
- [ ] Planear migración SQLite → PostgreSQL.
- [ ] Refactor de `Obra` para incluir `artista_id` + `galeria_id`.
- [ ] Middleware de aislamiento por `galeria_id`.
- [ ] URLs semánticas públicas.

---

## 8. CHEATSHEET DE COMANDOS

```powershell
# Levantar todo
docker compose up -d
docker compose logs -f

# Reiniciar servicios (cuando hay cambios en archivos)
docker compose restart backend
docker compose restart frontend

# Reset completo (PELIGROSO)
docker compose down -v
docker compose up -d --build

# Tests backend
cd backend; .\venv\Scripts\activate; pytest tests/ -v
del test_database.db 2>$null   # Reset BD de tests

# Instalar dependencias locales (para Pylance)
cd backend
pip install -r requirements.txt

# Git
git add .
git commit -m "tipo(ámbito): descripción" -m "Detalle opcional"
git push origin main
```

---

## 9. DECISIONES PENDIENTES

- [ ] **Multi-tenancy strategy**: Shared DB (recomendado MVP) vs Database-per-tenant (escala grande).
- [ ] **Roles extendidos**: ¿Agregar rol DUEÑO_GALERIA con permisos sobre suscripción?
- [ ] **Dominio y marca**: `artmanager.com` vs algo más descriptivo.
- [ ] **Deploy**: Railway / Fly.io / VPS propio.
- [ ] **CDN de imágenes**: Cloudflare R2 / AWS S3 en Fase 3.
- [ ] **Subdominios dinámicos**: Caddy vs Nginx con wildcard SSL.

---

## 10. CHANGELOG DE HITOS

### Día 4 — Cierre de Fase 2: Auth completo + Auditoría + Route Guards
- **Backend**: Modelo Usuario + JWT (access + refresh) + bcrypt.
- **Backend**: Endpoints /auth/register, /login, /refresh.
- **Backend**: Dependencias `get_current_user` y `require_role()`.
- **Backend**: Matriz de permisos aplicada a todos los routers (obras, técnicas, compradores, exposiciones, préstamos, dashboard).
- **Backend**: Endpoint GET /obras/publicas (catálogo velado sin datos sensibles).
- **Backend**: Tabla audit_logs + AuditService + endpoint GET /audit/logs (solo ADMIN).
- **Backend**: ~34 tests passing (incluyendo tests de auth, autorización y auditoría).
- **Frontend**: Landing page en `/` con SEO.
- **Frontend**: Catálogo velado en `/catalogo` (blur CSS, sin precios).
- **Frontend**: Catálogo privado en `/inventario` (precios, HD, filtros).
- **Frontend**: Login en `/login` + servicio `auth.ts` con localStorage.
- **Frontend**: Interceptor `httpClient.ts` (Bearer automático, SSR-safe, maneja 401/403).
- **Frontend**: HeaderNav como isla de React (UI adaptativa).
- **Frontend**: RouteGuard para proteger rutas privadas.
- **Arquitectura**: Aplicación de SOLID (Interface Segregation: PublicObra vs Obra).

### Día 2 — Cierre de Fase 1: CRUD completo + Dashboard
- Backend: PUT /obras/{id} con FormData + CRUD técnicas + filtros + dashboard.
- Frontend: Formulario edición, modal de eliminar, filtros con debounce, dashboard con Chart.js.
- Navegación global.

### Día 1 — MVP funcional + Tests
- Monorepo + Docker Compose + hot reload + suite de 15 tests.

---

*Fin del documento. Actualizar al cerrar cada fase.*