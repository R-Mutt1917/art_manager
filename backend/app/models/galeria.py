from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.artista import Artista
    from app.models.obra import Obra
    from app.models.usuario import UserGalleryRole
    from app.models.comprador import Comprador
    from app.models.prestamo import Prestamo
    from app.models.exposicion import Exposicion

class Galeria(SQLModel, table=True):
    """
    Galería de arte (tenant principal del sistema multi-tenant).
    """
    __tablename__ = "galerias"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Identificación
    nombre: str = Field(max_length=200, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)

    # Perfil público
    bio: Optional[str] = Field(default=None, max_length=2000)
    ubicacion: Optional[str] = Field(default=None, max_length=200)
    sitio_web: Optional[str] = Field(default=None, max_length=500)
    logo_url: Optional[str] = Field(default=None, max_length=500)

    # Estado
    activo: bool = Field(default=True, index=True)

    # Timestamps
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)

    # Relaciones
    artistas: List["Artista"] = Relationship(back_populates="galeria")
    obras: List["Obra"] = Relationship(back_populates="galeria")
    user_roles: List["UserGalleryRole"] = Relationship(back_populates="galeria") # <-- NUEVO
    compradores: List["Comprador"] = Relationship(back_populates="galeria")
    prestamos: List["Prestamo"] = Relationship(back_populates="galeria")
    exposiciones: List["Exposicion"] = Relationship(back_populates="galeria")