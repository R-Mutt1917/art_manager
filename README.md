# 🎨 Art Manager

**Plataforma SaaS profesional de gestión de arte para galerías latinoamericanas.**

Sistema integral de inventario, trazabilidad y gestión de obras de arte con autenticación
multi-usuario, auditoría completa y arquitectura preparada para escalar a multi-tenancy.

[![Tests](https://img.shields.io/badge/tests-33%20passed-brightgreen)]()
[![Backend](https://img.shields.io/badge/FastAPI-0.115+-blue)]()
[![Frontend](https://img.shields.io/badge/Astro-7.3+-purple)]()
[![License](https://img.shields.io/badge/license-Private-red)]()

---

## 📋 Tabla de Contenidos

- [Visión del Producto](#-visión-del-producto)
- [Características](#-características)
- [Arquitectura](#️-arquitectura)
- [Inicio Rápido](#-inicio-rápido)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Desarrollo](#-desarrollo)
- [Testing](#-testing)
- [Roadmap](#️-roadmap)
- [Documentación](#-documentación)

---

## 🎯 Visión del Producto

Art Manager reemplaza planillas Excel y cuadernos por un sistema profesional con:

- **Inventario visual** de obras con imágenes de alta resolución
- **Trazabilidad completa** (exposiciones, préstamos, ventas, provenance)
- **Gestión multi-usuario** con roles granulares (Admin, Curador, Asesor, Artista, Viewer)
- **Auditoría** de eventos críticos
- **Preparado para SaaS** multi-tenant (cada galería con su espacio aislado)

### Usuarios Objetivo
- Galerías medianas a grandes (Buenos Aires, CDMX, Bogotá, Santiago)
- Curadores independientes gestionando múltiples artistas
- Artistas consagrados con inventarios extensos
- Coleccionistas serios con portfolios

---

## ✨ Características

### Fase 1: CRUD Completo ✅
- ✅ Gestión de obras con subida de imágenes
- ✅ CRUD de técnicas, compradores, exposiciones, préstamos
- ✅ Filtros avanzados (estado, técnica, precio, búsqueda)
- ✅ Dashboard con métricas y gráficos
- ✅ Soft delete para preservar historial

### Fase 2: Autenticación y Seguridad ✅
- 🔐 JWT con access + refresh tokens
- 🔐 5 roles de usuario con permisos granulares
- 🔐 Catálogo público velado (sin precios ni imágenes HD)
- 🔐 Auditoría completa de eventos críticos
- 🔐 Route guards en frontend

### Fase 3: Multi-tenancy SaaS (Próximo) 🟠
- 🏢 Modelo de galerías aisladas
- 🎨 Gestión de artistas por galería
- 🔗 URLs semánticas (`/galeria-sur/artistas`)
- 💳 Planes de suscripción

---

## 🏗️ Arquitectura

```text
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Astro 7)                   │
│      SSR por defecto + Islas React para interactividad   │
│          Tailwind CSS v4 · Chart.js · Route Guards      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP (JSON + FormData)
                     │ Bearer Token (JWT)
┌────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                    │
│   Arquitectura en capas: Routers → Services → Models    │
│     SQLModel (SQLAlchemy + Pydantic) · JWT · bcrypt     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
   ┌─────▼─────┐┌────▼────┐┌─────▼─────┐
   │  SQLite   ││ Uploads ││   Auth    │
   │    DB     ││(Images) ││  Tokens   │
   └───────────┘└─────────┘└───────────┘
```

### Principios de Diseño
- **Separación de responsabilidades**: Backend y frontend independientes
- **SSR por defecto**: Performance y SEO optimizados
- **API-first**: Frontend consume endpoints RESTful
- **Seguridad por defecto**: Rutas protegidas, tokens JWT, auditoría
- **Escalabilidad**: Preparado para migrar a PostgreSQL + multi-tenancy

---

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker Desktop instalado y corriendo
- Git
- (Opcional) Node.js 20+ y Python 3.12+ para desarrollo local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/R-Mutt1917/art_manager.git
cd art_manager
```

### 2. Levantar con Docker Compose
```bash
docker compose up -d
```
Esto levanta:
- **Backend:** http://localhost:8000 (API + Swagger en `/docs`)
- **Frontend:** http://localhost:4321 (UI)

### 3. Acceder a la Aplicación
Abrí http://localhost:4321 en tu navegador:
- Verás la landing page
- Hacé clic en "Iniciar Sesión"
- Usá las credenciales de desarrollo:
  - **Email:** admin@artmanager.com
  - **Password:** admin123

### 4. Explorar
- `/catalogo` → Catálogo público (velado, sin precios)
- `/inventario` → Catálogo privado (con filtros, precios, imágenes HD)
- `/dashboard` → Métricas y gráficos
- `/crear` → Crear nueva obra
- http://localhost:8000/docs → Documentación Swagger de la API

---

## 📂 Estructura del Proyecto

```text
art_manager/
├── backend/                 # API RESTful (FastAPI + SQLModel)
│   ├── app/
│   │   ├── core/           # Configuración, seguridad, dependencias
│   │   ├── models/         # Entidades SQLModel
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   ├── routers/        # Endpoints HTTP
│   │   ├── seed.py         # Datos iniciales
│   │   └── main.py         # Entry point
│   ├── tests/              # 33 tests passing
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # UI (Astro 7 + React islands)
│   ├── src/
│   │   ├── components/     # Componentes reutilizables
│   │   ├── layouts/        # Layouts globales
│   │   ├── pages/          # Rutas (file-based routing)
│   │   └── services/       # Cliente HTTP + auth
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml      # Orquestación de servicios
├── .gitignore
└── README.md              # Este archivo
```

---

## 🛠️ Desarrollo

### Opción A: Todo con Docker (Recomendado)
```bash
# Levantar servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Reiniciar un servicio (después de cambios)
docker compose restart backend
docker compose restart frontend

# Detener (conserva datos)
docker compose down

# Reset completo (BORRA base de datos y uploads)
docker compose down -v
docker compose up -d --build
```

### Opción B: Desarrollo Local (sin Docker)

#### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend (en otra terminal):
```bash
cd frontend
pnpm install
pnpm dev
```

---

## 🧪 Testing

### Backend (33 tests)
```bash
cd backend
venv\Scripts\activate  # Activar venv

# Resetear BD de tests
del test_database.db 2>$null  # Windows
# rm -f test_database.db      # Mac/Linux

# Correr todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=app --cov-report=term-missing
```

#### Suite actual:
- ✅ **Auth:** 8 tests
- ✅ **Obras:** 11 tests
- ✅ **Técnicas:** 4 tests
- ✅ **Compradores:** 2 tests
- ✅ **Exposiciones:** 3 tests
- ✅ **Préstamos:** 2 tests
- ✅ **Auditoría:** 3 tests

### Frontend
```bash
cd frontend
pnpm astro check  # Validación de tipos
```

---

## 🔐 Seguridad

### Autenticación
- *bcrypt* para hash de contraseñas
- *JWT* con access (30 min) + refresh (7 días) tokens
- **5 roles:** ADMIN, CURADOR, ASESOR, ARTISTA, VIEWER

### Autorización
- Matriz de permisos granular por endpoint
- Dependencias `get_current_user` + `require_role()`
- Catálogo público velado (sin datos sensibles)

### Auditoría
- Tabla `audit_logs` con eventos críticos
- Login exitoso/fallido, registro, creación/edición de obras
- Endpoint `/audit/logs` solo para ADMIN

### Mejores Prácticas
- ✅ *Soft delete* en todas las entidades
- ✅ Validación con *Pydantic* en schemas
- ✅ *CORS* configurado para frontend
- ⚠️ En producción: migrar tokens a cookies *httpOnly*

---

## 🗺️ Roadmap

### ✅ Fase 1: CRUD Completo (Completada)
- Gestión de obras, técnicas, compradores, exposiciones, préstamos
- Filtros avanzados y dashboard con métricas
- Subida de imágenes con validación

### ✅ Fase 2: Autenticación y Roles (Completada)
- JWT con access + refresh tokens
- 5 roles de usuario con permisos granulares
- Auditoría de eventos críticos
- Catálogo público velado
- Route guards en frontend

### 🟠 Fase 3: Multi-tenancy SaaS (En Desarrollo)
- Modelo de galerías aisladas
- Gestión de artistas por galería
- URLs semánticas (`/galeria-sur/artistas`)
- Migración SQLite → PostgreSQL
- Onboarding self-service
- Planes de suscripción

### 🔵 Fase 4: Features de Dominio (Planificado)
- Certificados de autenticidad en PDF con QR
- Provenance (timeline de la obra)
- Condition reports (fotos antes/después)
- Sistema de ofertas y negociación
- Modo "Viewing Room" (3D virtual)

### 🟣 Fase 5: IA Aplicada (Planificado)
- Auto-clasificación de técnica/estilo (GPT-4 Vision)
- Descripción curatorial automática
- Valuación asistida por comparables (RAG)
- Detección de atribución
- Recomendación obra ↔ exposición

---

## 📚 Documentación
- **Backend README** — API, endpoints, testing
- **Frontend README** — UI, componentes, rutas
- **Project Context** — Visión completa del proyecto
- **API Docs** — Swagger interactivo

---

## 🤝 Contribución
Proyecto privado en desarrollo activo. Para contribuir:
1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer cambios y commitear: `git commit -m "feat: descripción"`
3. Push a la rama: `git push origin feature/nueva-funcionalidad`
4. Abrir Pull Request

#### Convención de commits (Conventional Commits):
- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `docs:` cambios en documentación
- `refactor:` refactorización de código
- `test:` agregar o modificar tests

---

## 📄 Licencia
Privado — Uso interno y desarrollo de producto SaaS.

---

## 📞 Contacto
- **Desarrollador:** Matías
- **Email:** [email](matiaszelarayandev@gmail.com)
- **Repositorio:** https://github.com/R-Mutt1917/art_manager

Construido con ❤️ para la comunidad del arte latinoamericano.
