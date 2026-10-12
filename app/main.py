from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.models import *
from app.database import create_db_and_tables
from app.routers import obras, tecnicas, exposiciones, compradores
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta al iniciar la aplicación."""
    print("🔄 Creando tablas de la base de datos...")
    create_db_and_tables()
    print("✅ Base de datos lista.")
    yield

app = FastAPI(
    title="Gestor de Obras de Arte",
    description="API para gestionar inventario, exposiciones y trazabilidad de arte.",
    version="1.0.0",
    lifespan=lifespan,
)

# Montar la carpeta de uploads como archivos estáticos
# Esto permite acceder a las imágenes vía URL: http://127.0.0.1:8000/uploads/nombre_archivo.jpg
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 3. Registrar los routers (¡ESTO ES LO IMPORTANTE!)
app.include_router(obras.router)
app.include_router(tecnicas.router)
app.include_router(exposiciones.router)
app.include_router(compradores.router)
@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "Bienvenido al Gestor de Obras de Arte ",
        "documentacion": "/docs",
    }