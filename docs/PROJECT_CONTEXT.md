# ART MANAGER — Documento Maestro de Proyecto y Roadmap

> **Propósito de este documento:** Ser la fuente única de verdad del proyecto.
> Cualquier developer o IA que continúe el trabajo DEBE leer esto primero.
> **Regla de oro:** Al cerrar cada fase o hito, actualizar este documento (sección Changelog).

---

## 1. VISIÓN DEL PRODUCTO

**Art Manager** es un sistema de gestión integral para galerías de arte y artistas visuales:
inventario de obras con imágenes, técnicas, ventas, compradores, exposiciones y préstamos
con trazabilidad completa (provenance).

**Propuesta de valor:** Reemplazar planillas Excel y cuadernos por un sistema con
trazabilidad profesional, y a futuro, inteligencia artificial aplicada al mercado del arte.

**Usuarios objetivo (roles previstos, ver Fase 2):**
Admin (galerista) · Curador · Asesor de ventas · Artista · Coleccionista · Público.

---

## 2. STACK TÉCNICO

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Backend | FastAPI + SQLModel + SQLite | Arquitectura en capas: routers → services → models |
| Frontend | Astro 7 (SSR) + React islands + Tailwind CSS v4 | Islas React solo donde hay interactividad |
| Infra | Docker Compose | Hot reload real en ambos servicios |
| Testing | pytest + fastapi.TestClient | 18/18 tests pasando |
| Gestores | pnpm (front) / pip + venv (back, solo para tests locales) | |

### Estructura del monorepo
```
art_manager/
├── docker-compose.yml # backend + frontend, bind mounts (¡NO volúmenes sobre /app!)
├── backend/
│ ├── app/
│ │ ├── main.py # lifespan: crea tablas + seed; CORS; mount /uploads
│ │ ├── database.py # engine, get_session, create_db_and_tables
│ │ ├── seed.py # 7 técnicas comunes al arrancar
│ │ ├── core/config.py # settings (UPLOAD_DIR, etc.)
│ │ ├── models/ # Obra, Tecnica, Comprador, Exposicion, Prestamo
│ │ ├── schemas/ # Pydantic: Create/Update/Read por entidad
│ │ ├── services/ # Lógica de negocio (ObraService, DashboardService, image_service, etc.)
│ │ └── routers/ # obras, tecnicas, compradores, exposiciones, prestamos, dashboard
│ └── tests/ # test_obras (9), test_tecnicas, test_compradores, test_exposiciones, test_prestamos
└── frontend/
└── src/
├── pages/ # index.astro, obras/[id].astro, obras/[id]/editar.astro, crear.astro, dashboard.astro, tecnicas/
├── components/ # ArtworkForm.tsx, CatalogFilters.tsx, DashboardCharts.tsx, DeleteArtworkButton.tsx
├── layouts/ # Layout.astro (con navegación global)
└── services/api.ts # fetch server-side (usa API_URL)
```

### Variables de entorno (CRÍTICO, no tocar sin leer)
- `PUBLIC_API_URL=http://localhost:8000` → código que corre en el **navegador** (React).
- `API_URL=http://backend:8000` → código que corre en el **servidor** (Astro SSR, red interna Docker).
- Definidas en `docker-compose.yml` (environment) y en `frontend/.env` (desarrollo local).

---

## 3. ESTADO ACTUAL — LO QUE FUNCIONA ✅

### Backend
- CRUD de obras con **subida de imagen** (multipart/form-data) y **upsert de técnica por nombre**:
  si la técnica no existe, se crea automáticamente en el mismo request.
- **PUT de obras** acepta FormData (permite reemplazar imagen en la misma operación).
- Seed automático de 7 técnicas al arrancar (lifespan).
- Soft delete de obras y compradores.
- **CRUD completo de técnicas** con validación: no se puede eliminar si tiene obras asociadas.
- Ventas (`/compradores/ventas/registrar`) que cambian estado de obra a `vendida`.
- Exposiciones con validación de superposición de fechas + checklist de retiro.
- Préstamos con ciclo completo (crear → devolución) y validación de obra vendida.
- **Filtros avanzados en GET /obras/**: estado, técnica, rango de precio, búsqueda en título/notas.
- **Dashboard con métricas agregadas**: totales, obras por estado, valor de inventario, top técnicas.
- Servido de imágenes estáticas en `/uploads`.
- CORS habilitado (`allow_origins=["*"]`).

### Frontend
- **Catálogo SSR en `/`** con tarjetas de obras y **toolbar compacta de filtros** (búsqueda con debounce, técnica, estado, precio).
- **Detalle de obra en `/obras/[id]`** con técnica y comprador resueltos server-side, botón de edición y eliminación con modal de confirmación.
- **Formulario de creación/edición en `/crear` y `/obras/[id]/editar`**: autocomplete accesible de técnicas (crea on-the-fly),
  subida de imagen con preview de nombre/peso, validaciones y mensajes de éxito/error.
- **Listado de técnicas en `/tecnicas`** con edición y eliminación (valida obras asociadas).
- **Dashboard en `/dashboard`** con KPI cards (total obras, valor inventario, total vendido, disponibles) y gráficos Chart.js (pie de estados, bar de top técnicas).
- **Navegación global** en Layout: Obras, Dashboard, Técnicas, Exposiciones, + Nueva Obra.

### Tests: 18/18 PASSED
- test_obras.py (9): crear, crear con imagen, upsert técnica, 422 sin técnica, listar, soft delete, **PUT conserva imagen**, **PUT con técnica nueva**, **PUT 404**.
- test_tecnicas.py (2), test_compradores.py (2), test_exposiciones.py (3), test_prestamos.py (2).

---

## 4. CONTRATO REAL DE LA API (referencia rápida)

### Obras
| Método | Ruta | Body | Notas |
|--------|------|------|-------|
| POST | `/obras/` | **FormData**: titulo, anio, dimensiones, precio?, estado?, notas?, **tecnica (NOMBRE, upsert)**, imagen? (file) | 201 |
| GET | `/obras/` | query: `estado`, `tecnica_id`, `precio_min`, `precio_max`, `busqueda` | Filtros avanzados |
| GET | `/obras/{id}` | — | 404 si inactiva |
| PUT | `/obras/{id}` | **FormData** (igual que POST, imagen opcional) | Reemplaza imagen si viene |
| DELETE | `/obras/{id}` | — | Soft delete |
| POST | `/obras/{id}/imagen` | file | Reemplaza y borra la anterior del disco |
| DELETE | `/obras/{id}/imagen` | — | Deja la obra sin foto |

### Técnicas
| Método | Ruta | Body | Notas |
|--------|------|------|-------|
| GET | `/tecnicas/` | — | Lista todas |
| POST | `/tecnicas/` | JSON TecnicaCreate | 201 |
| GET | `/tecnicas/{id}` | — | 404 si no existe |
| PUT | `/tecnicas/{id}` | JSON TecnicaUpdate | Parcial |
| DELETE | `/tecnicas/{id}` | — | **400 si tiene obras asociadas** |

### Compradores
`POST/GET /compradores/` · `GET/PUT/DELETE /compradores/{id}` ·
`GET /compradores/{id}/compras` · `POST /compradores/ventas/registrar`
(body: `obra_id`, `comprador_id`, `fecha_venta`)

### Exposiciones
`POST /exposiciones/` (**requiere campo `lugar`**) ·
`POST /exposiciones/{id}/obras/{obra_id}` (body AsignarObraSchema; valida superposición) ·
`GET /exposiciones/{id}/checklist` (es GET, no POST)
⚠️ Asignar una obra NO cambia su estado a `en_exposicion` (decisión de diseño vigente).

### Préstamos
`POST /prestamos/` (**requiere**: `prestatario_nombre`, `fecha_prestamo`, `fecha_devolucion_esperada`) ·
`POST /prestamos/{id}/devolucion` (**requiere** `fecha_devolucion_real`) ·
`GET /prestamos/activos`

### Dashboard
| Método | Ruta | Notas |
|--------|------|-------|
| GET | `/dashboard/stats` | Retorna JSON con: `total_obras`, `obras_por_estado`, `valor_inventario`, `total_vendido`, `top_tecnicas` |

### Estados de obra (enum EstadoObra)
`disponible` · `vendida` · `en_exposicion` · `en_prestamo`

---

## 5. LECCIONES APRENDIDAS / TRAMPAS CONOCIDAS 🕳️

1. **NUNCA montar un volumen nombrado sobre `/app`** (pasó con `db_data:/app`): tapa el código
   del bind mount, congela la app y rompe el hot reload. Los volúmenes van solo sobre subcarpetas
   de datos (`upload_data:/app/app/uploads`).
2. **CORS:** el navegador bloquea fetch cross-origin; el SSR de Astro no. Por eso existen DOS
   variables de API URL (ver §2). Si aparece "Failed to fetch" en React, revisar CORS y PUBLIC_API_URL.
3. **React en .tsx:** usar `className` (no `class`) y `import { type FormEvent }` con
   `verbatimModuleSyntax` habilitado.
4. **Tests:** el POST y PUT de obras son FormData (`data=` + `files=`), NO JSON. Los tests viejos con
   `json=` y `tecnica_id` quedan obsoletos al cambiar el contrato.
5. **Pylance "sqlmodel no definido":** seleccionar el interpreter del venv de backend en VS Code.
6. **Deuda técnica conocida (warnings):** `datetime.utcnow()` deprecado (migrar a
   `datetime.now(datetime.UTC)`) y `session.query()` en seed.py (usar `session.exec()`).
7. **Reset nuclear controlado:** `docker compose down -v` borra BD y volúmenes; usar solo a conciencia.
8. **Enums en Python:** los miembros se acceden con MAYÚSCULAS (`EstadoObra.DISPONIBLE`), no minúsculas. El `.value` es el string.
9. **Astro y rutas dinámicas:** crear carpetas nuevas (`[id]/`) con el servidor corriendo a veces requiere `docker compose restart frontend` para que el watcher las registre.
10. **React y SVG:** en JSX usar camelCase (`strokeWidth`, `strokeLinecap`), en .astro usar kebab-case (`stroke-width`).

---

## 6. ROADMAP POR FASES

### ✅ FASE 1 — CRUD completo y pulido (COMPLETADA)
- [x] F1.1 Editar obra: página `/obras/[id]/editar` con form React prellenado → PUT con FormData.
- [x] F1.2 Eliminar obra desde UI con modal de confirmación → DELETE (soft).
- [x] F1.3 Reemplazar / eliminar imagen desde el formulario de edición (PUT ya lo maneja).
- [x] F1.4 CRUD de técnicas en UI (listar, editar, eliminar con aviso si tiene obras).
- [x] F1.5 Filtros de catálogo: técnica, estado, rango de precio, búsqueda (query params + debounce).
- [x] F1.6 Dashboard `/dashboard`: KPI cards + gráficos Chart.js (pie de estados, bar de técnicas).
- [ ] F1.7 (OPCIONAL) Página `/exposiciones` en el front (hoy da 404): listar, crear, asignar obras, checklist.
- [ ] F1.8 (OPCIONAL) Limpieza de warnings (utcnow, session.query) + tests adicionales.

### 🟡 FASE 2 — Autenticación y roles (SIGUIENTE PRIORIDAD)
- Modelo `Usuario` (email único, hash bcrypt/argon2, rol enum) + JWT access/refresh.
- Dependencias de autorización (`require_role(...)`) por endpoint.
- Matriz de permisos: Admin (todo) · Curador (catálogo+exposiciones) · Ventas (ventas+compradores) ·
  Artista (sus obras) · Coleccionista (catálogo público+su historial) · Público (solo ver).
- Páginas `/login`, protección de rutas, logout; tests de autorización (401/403).

### 🟠 FASE 3 — Features de dominio de arte
- Certificados de autenticidad en PDF con QR (reportlab/weasyprint).
- Provenance: línea de tiempo de la obra (ventas, exposiciones, préstamos) en el detalle.
- Condition reports con fotos antes/después de préstamos.
- Ofertas y negociación de coleccionistas.
- Export para ferias (ARCO/Art Basel) y "viewing room" (Three.js, opcional).
- Multi-tenant (varias galerías) solo si se encara como SaaS.

### 🔵 FASE 4 — IA aplicada al arte visual
- Auto-clasificación de técnica/estilo al subir imagen (GPT-4 Vision / CLIP).
- Descripción curatorial automática (LLM con prompt de catálogo de museo).
- Valuación asistida por comparables (RAG sobre datos de ventas propios + públicos).
- Recomendación obra ↔ exposición (embedding de imágenes + metadatos).
- Detección de anomalías de atribución (comparación con corpus del artista).
- ⚠️ Requiere Fase 2 antes (control de costo y abuso de las llamadas a IA).

---

## 7. PRÓXIMAS TAREAS INMEDIATAS (elegir una por sesión)

**Opción A — Autenticación (Fase 2, recomendada):**
Implementar modelo Usuario + JWT + middleware de autorización. Empezar con 2 roles (Admin/Curador) y proteger endpoints críticos. Esto habilita todo lo demás.

**Opción B — Cambio de estado manual (F1.7 opcional):**
Agregar dropdown simple en `/obras/[id]` para cambiar estado (disponible/vendida/en_exposicion/en_prestamo) con PUT. Solución "parche" que después reemplazamos en Fase 3 por acciones ricas (registrar venta con comprador, asignar a exposición con fechas, etc.).

**Opción C — Auto-clasificación IA (Fase 4 puntual, el "wow factor"):**
Botón "Analizar con IA" en el form que envía la imagen a GPT-4 Vision y prellena técnica + descripción + año estimado. Requiere clave de API por variable de entorno en el backend (proxy), nunca en el front.

---

## 8. CHEATSHEET DE COMANDOS

```powershell
# Levantar todo (desde la raíz)
docker compose up -d            # sin --build salvo cambios en Dockerfile/requirements/package.json
docker compose logs -f          # ver ambos servicios
docker compose down             # detener (conserva datos)
docker compose down -v          # ⚠️ borra BD y uploads

# Tests backend (fuera de Docker, con venv)
cd backend; .\venv\Scripts\activate; pytest tests/ -v

# Git
git add . ; git commit -m "tipo(ámbito): descripción" ; git push origin main
```


## 9. DECISIONES PENDIENTES

- Estrategia general: A (consolidar: F1→F2→IA puntual, recomendada) · B (IA first) · C (SaaS/multi-tenant).
- Roles reales según el caso de uso concreto del dueño del producto.
- Deploy: Railway / Fly.io / VPS; y migración SQLite → PostgreSQL para producción.
- Dominio y marca del producto.

## 10. CHANGELOG DE HITOS

### Día 2 — Cierre de Fase 1: CRUD completo + Dashboard
- **Backend**: PUT /obras/{id} con FormData (reemplazo de imagen en la misma operación) + 3 tests nuevos (9/9 en test_obras.py).
- **Backend**: CRUD completo de técnicas con validación de obras asociadas (no se puede borrar si tiene obras).
- **Backend**: Filtros avanzados en GET /obras/ (estado, técnica, precio, búsqueda en título/notas).
- **Backend**: DashboardService con métricas agregadas (totales, valor inventario, top técnicas) + endpoint GET /dashboard/stats.
- **Frontend**: Formulario de edición reutilizable (ArtworkForm con modo create/edit).
- **Frontend**: Botón de eliminación con modal de confirmación (DeleteArtworkButton).
- **Frontend**: Toolbar compacta de filtros con debounce (CatalogFilters).
- **Frontend**: Dashboard con KPI cards + Chart.js (pie de estados, bar de técnicas).
- **Frontend**: Navegación global en Layout (Obras, Dashboard, Técnicas, Exposiciones, + Nueva Obra).
- **Arquitectura**: Decisión de mover gestión de imagen al formulario de edición (mejor separación de concerns).

### Día 1 — MVP funcional + Tests
- Monorepo + Docker Compose + hot reload real · fix bug GET /tecnicas/{id} con TDD ·
SSR del detalle de obra · formulario de creación con upsert de técnica e imagen ·
CORS + fix volumen shadowing · seed automático · **suite de 15/15 tests**.

Fin del documento. Actualizar al cerrar cada fase.