# 🎨 Art Manager API

API RESTful para la gestión de inventario, portafolio y trazabilidad de obras de arte para artistas independientes y curadores.

## 🚀 Tecnologías Utilizadas
- **Python 3.12+**
- **FastAPI**: Framework web moderno y de alto rendimiento.
- **SQLModel / SQLAlchemy**: ORM para la gestión de base de datos (SQLite para desarrollo, escalable a PostgreSQL).
- **Pydantic V2**: Validación de datos y configuración.
- **Arquitectura en Capas**: Separación clara entre Routers (HTTP), Services (Lógica de Negocio) y Models (Base de Datos).

## ✨ Características Principales
- ✅ CRUD completo de Obras de Arte y Técnicas.
- ✅ **Soft Delete**: Borrado lógico para preservar la integridad referencial y el historial.
- ✅ Gestión de Imágenes: Subida, validación (tipo/tamaño), reemplazo y eliminación segura de archivos.
- ✅ Filtrado avanzado por estado y técnica.
- ✅ Documentación automática interactiva (Swagger UI).

## 🛠️ Instalación y Ejecución Local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/R-Mutt1917/art_manager.git
   cd art_manager
2. Crea y activa un entorno virtual: 
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta el servidor de desarrollo:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
5. Accede a la documentación interactiva en tu navegador:
    ```bash
    http://127.0.0.1:8000/docs
    ```

## 📂 Estructura del Proyecto

```bash
    art_manager/
    ├── app/
    │   ├── core/         # Configuración y variables de entorno
    │   ├── models/       # Modelos de base de datos (SQLModel)
    │   ├── schemas/      # Esquemas de validación (Pydantic)
    │   ├── services/     # Lógica de negocio y reglas de dominio
    │   ├── routers/      # Endpoints de la API (Capa HTTP)
    │   └── uploads/      # Almacenamiento local de imágenes (Ignorado en Git)
    ├── tests/            # Pruebas unitarias y de integración
    ├── .gitignore
    ├── requirements.txt
    └── README.md
```

