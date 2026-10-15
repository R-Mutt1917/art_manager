from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.database import engine, create_db_and_tables
from app.models import *  # noqa: F401,F403 - registra todos los modelos
from app.routers import obras, tecnicas, exposiciones, compradores, prestamos
from app.seed import seed_database
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Creando tablas de la base de datos...")
    create_db_and_tables()
    print("✅ Base de datos lista.")

    with Session(engine) as session:
        seed_database(session)

    yield


app = FastAPI(
    title="Gestor de Obras de Arte",
    description="API para gestionar inventario, exposiciones y trazabilidad de arte.",
    version="1.0.0",
    lifespan=lifespan,
)

# =====================================================
# CORS: autoriza al frontend (navegador) a consumir la API
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =====================================================

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(obras.router)
app.include_router(tecnicas.router)
app.include_router(exposiciones.router)
app.include_router(compradores.router)
app.include_router(prestamos.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "Bienvenido al Gestor de Obras de Arte 🎨",
        "documentacion": "/docs",
    }