from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped

# Imports solo para chequeo de tipos (evita import circular en runtime)
if TYPE_CHECKING:
    from app.models.tecnica import Tecnica
    from app.models.comprador import Comprador
    from app.models.prestamo import Prestamo
    from app.models.obra_exposicion import ObraExposicion
    from app.models.artista import Artista
    from app.models.galeria import Galeria

class EstadoObra(str, Enum):
    DISPONIBLE = "disponible"
    VENDIDA = "vendida"
    EN_EXPOSICION = "en_exposicion"
    EN_PRESTAMO = "en_prestamo"

class Obra(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True, max_length=200)
    anio: int = Field(ge=1000, le=9999)
    dimensiones: str = Field(max_length=50)
    precio: Optional[float] = Field(default=None, ge=0)
    estado: EstadoObra = Field(default=EstadoObra.DISPONIBLE)
    imagen_url: Optional[str] = Field(default=None)
    notas: Optional[str] = Field(default=None)
    fecha_venta: Optional[date] = Field(default=None)

    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    activo: bool = Field(default=True)

    # ---- MULTI-TENANCY (Fase 3, Tarea 3) ----
    # Nullable en esta fase para no romper los 40 tests existentes.
    # En T4 migraremos los datos existentes a la "Galería Demo".
    galeria_id: Optional[int] = Field(default=None, foreign_key="galerias.id", index=True)
    artista_id: Optional[int] = Field(default=None, foreign_key="artistas.id", index=True)

    tecnica_id: Optional[int] = Field(default=None, foreign_key="tecnica.id")
    tecnica: Mapped[Optional["Tecnica"]] = Relationship(back_populates="obras")

    comprador_id: Optional[int] = Field(default=None, foreign_key="comprador.id")
    comprador: Mapped[Optional["Comprador"]] = Relationship(back_populates="obras")

    prestamo: Mapped[Optional["Prestamo"]] = Relationship(back_populates="obra")
    exposiciones: Mapped[List["ObraExposicion"]] = Relationship(back_populates="obra")

    # Relaciones de multi-tenancy
    galeria: Mapped[Optional["Galeria"]] = Relationship(back_populates="obras")
    artista: Mapped[Optional["Artista"]] = Relationship(back_populates="obras")