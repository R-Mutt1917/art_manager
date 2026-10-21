# 🎨 Art Manager API

API RESTful profesional para gestión de inventario, portafolio y trazabilidad de obras de arte.
Diseñada para galerías, curadores independientes y artistas visuales con enfoque en seguridad,
trazabilidad completa y preparada para escalar a plataforma SaaS multi-tenant.

## 🚀 Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Framework | FastAPI | 0.115+ |
| Lenguaje | Python | 3.12+ |
| ORM | SQLModel (SQLAlchemy + Pydantic) | — |
| Base de datos | SQLite (dev) → PostgreSQL (prod) | — |
| Autenticación | PyJWT + bcrypt | — |
| Testing | pytest + FastAPI TestClient | — |
| Configuración | pydantic-settings | V2 |

## ✨ Características Principales

### Core
- ✅ **CRUD completo de obras** con subida de imágenes (multipart/form-data)
- ✅ **Soft delete** en todas las entidades (preserva historial)
- ✅ **Upsert automático de técnicas** (se crean on-the-fly si no existen)
- ✅ **Filtrado avanzado** por estado, técnica, precio, búsqueda
- ✅ **Dashboard con métricas** agregadas (Chart.js-ready)
- ✅ **Documentación Swagger** automática en `/docs`

### Seguridad (Fase 2)
- 🔐 **Autenticación JWT** con access + refresh tokens
- 🔐 **5 roles de usuario**: ADMIN, CURADOR, ASESOR, ARTISTA, VIEWER
- 🔐 **Autorización granular** por endpoint (matriz de permisos)
- 🔐 **Catálogo público velado** (`/obras/publicas` sin datos sensibles)
- 🔐 **Auditoría completa** (tabla `audit_logs` con eventos críticos)
- 🔐 **Seed automático** de usuario admin al arrancar

## 📂 Estructura del Proyecto

```bash
backend/
├── app/
│ ├── core/
│ │ ├── config.py # Pydantic Settings (JWT, DB, etc.)
│ │ ├── security.py # bcrypt + PyJWT (hash + tokens)
│ │ └── dependencies.py # get_current_user + require_role
│ ├── models/ # SQLModel entities
│ │ ├── obra.py
│ │ ├── tecnica.py
│ │ ├── comprador.py
│ │ ├── exposicion.py
│ │ ├── prestamo.py
│ │ ├── usuario.py # Fase 2: roles + auth
│ │ └── audit_log.py # Fase 2: auditoría
│ ├── schemas/ # Pydantic (Create/Update/Read)
│ ├── services/ # Lógica de negocio
│ │ ├── obra_service.py
│ │ ├── auth_service.py # Fase 2
│ │ ├── audit_service.py # Fase 2
│ │ └── ...
│ ├── routers/ # Endpoints HTTP
│ │ ├── obras.py
│ │ ├── tecnicas.py
│ │ ├── auth.py # Fase 2: register/login/refresh
│ │ ├── audit.py # Fase 2: GET /audit/logs (ADMIN only)
│ │ └── ...
│ ├── seed.py # Seed técnicas + admin user
│ └── main.py # Entry point + lifespan + CORS
├── tests/ # 33 tests passing
│ ├── conftest.py # Fixtures (test isolation + auth_headers)
│ ├── test_auth.py # 8 tests
│ ├── test_obras.py # 11 tests
│ ├── test_audit.py # 3 tests
│ └── ...
├── uploads/ # Imágenes subidas (gitignored)
├── database.db # SQLite dev (gitignored)
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🛠️ Instalación y Ejecución

### Opción A: Desarrollo Local (sin Docker)

```bash
# 1. Clonar y entrar al directorio
cd backend

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear archivo .env (opcional, valores por defecto funcionan)
cp .env.example .env

# 6. Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción B: Con Docker Compose (recomendado)
```bash
# Desde la raíz del monorepo
docker compose up -d backend

# Ver logs
docker compose logs -f backend
```
## 📚 Endpoints Principales

### Autenticación (público)
| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| **POST** | `/auth/register` | Registro (siempre crea `VIEWER`) |
| **POST** | `/auth/login` | Login → *access* + *refresh* tokens |
| **POST** | `/auth/refresh` | Renovar tokens |

---

### Obras

| Método | Ruta | Auth | Descripción |
| :--- | :--- | :--- | :--- |
| **GET** | `/obras/` | Público | Con filtros avanzados |
| **GET** | `/obras/publicas` | Público | Catálogo velado (sin precios ni imágenes HD) |
| **GET** | `/obras/{id}` | Público | Detalle completo |
| **POST** | `/obras/` | `ADMIN` / `CURADOR` | *FormData* (imagen + metadata) |
| **PUT** | `/obras/{id}` | `ADMIN` / `CURADOR` | *FormData* (reemplaza imagen si viene) |
| **DELETE** | `/obras/{id}` | `ADMIN` / `CURADOR` | *Soft delete* |

---

### Auditoría (Solo ADMIN)

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| **GET** | `/audit/logs` | Listar eventos (`limit`, `tipo_evento`) |

---

> 💡 **Documentación completa interactiva:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Testing
```bash
# Activar venv
cd backend
venv\Scripts\activate  # Windows

# Resetear BD de tests y correr suite completa
del test_database.db 2>$null  # Windows
# rm -f test_database.db      # Mac/Linux
pytest tests/ -v

# Con coverage
pytest tests/ --cov=app --cov-report=term-missing
```
### Suite actual: 33 tests passing

#### Detalles de la suite
* Auth: **8 tests**
* Obras: **11 tests** (incluye autorización)
* Técnicas: **4 tests**
* Compradores: **2 tests**
* Exposiciones: **3 tests**
* Préstamos: **2 tests**
* Auditoría: **3 tests**

---

### 🔐 Seguridad

#### Autenticación
* **Algoritmo de hash:** *bcrypt* para contraseñas con un *cost factor* de **12**.
* **Firma de tokens:** *PyJWT* configurado con **RS256** (asimétrico) o **HS256** (simétrico).
* **Access token:** Duración y vida útil de **30 minutos**.
* **Refresh token:** Duración y vida útil de **7 días**.

#### Autorización (Matriz de Permisos)

| Acción | ADMIN | CURADOR | ASESOR | ARTISTA | VIEWER |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CRUD Obras** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **CRUD Técnicas** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Compradores + Ventas** | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Exposiciones** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Préstamos** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Dashboard** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Ver catálogo público** | ✅ | ✅ | ✅ | ✅ | ✅ |

#### Auditoría
Todos los eventos críticos como logins, registros, creación o edición de obras y ventas se guardan en `audit_logs` con los siguientes datos:
* **Usuario:** ID y correo electrónico denormalizado.
* **Timestamp:** Fecha y hora exacta del suceso.
* **IP address:** Dirección de red del cliente.
* **Tipo de evento:** Acción específica realizada.
* **Entidad afectada:** Recurso que sufrió la modificación.

## 🔧 Configuración

### Variables de entorno (`.env`)
```Bash
# Base de datos
DATABASE_URL=sqlite:///./database.db

# JWT
SECRET_KEY=tu-clave-super-secreta-de-32-caracteres-minimo
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Uploads
UPLOAD_DIR=./app/uploads
MAX_UPLOAD_SIZE=10485760  # 10 MB

# CORS
ALLOWED_ORIGINS=http://localhost:4321
```

---

## 🚢 Producción

### Para deploy en producción:
* **Migrar a PostgreSQL** (recomendado para multi-tenancy).
* **Variables de entorno seguras** (no commitear `.env`).
* **SECRET_KEY fuerte** (32+ caracteres aleatorios).
* **HTTPS obligatorio** (LetsEncrypt o similar).
* **Rate limiting** en `/auth/login` (protección fuerza bruta).
* **Cookies httpOnly** en lugar de localStorage (contra XSS).
* **Backups automáticos** de la base de datos.

---

## 🗺️ Roadmap

* **✅ Fase 1:** CRUD completo + dashboard.
* **✅ Fase 2:** Auth + roles + auditoría.
* **🟠 Fase 3 (Próximo):** Multi-tenancy SaaS aplicando los modelos de **Galería** y **Artista**.
* **🔵 Fase 4:** Características avanzadas de dominio como **certificados PDF**, *provenance* y *condition reports*.
* **🟣 Fase 5:** Integración de **IA aplicada** para clasificación automática y generación de descripciones curatoriales.

---

## 📄 Licencia

**Privado** — Destinado únicamente para uso interno y el desarrollo del producto SaaS.

* **Contacto:** [email@dominio.com](matiaszelarayandev@gmail.com)
* **Repositorio:** [://github.com](https://github.com/R-Mutt22)