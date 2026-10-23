from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.galeria import Galeria
    from app.models.obra import Obra


class Artista(SQLModel, table=True):
    """
    Artista perteneciente a una galería (tenant).

    El slug es único DENTRO de cada galería (no globalmente),
    para permitir URLs semánticas como:
      /galeria-sur/julio-le-parc
      /galeria-norte/julio-le-parc   (otro artista con mismo slug, otra galería)
    """
    __tablename__ = "artistas"
    __table_args__ = (
        UniqueConstraint("galeria_id", "slug", name="uq_artista_galeria_slug"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # Tenant: a qué galería pertenece (corazón del aislamiento de datos)
    galeria_id: int = Field(foreign_key="galerias.id", index=True)

    # Identificación
    nombre: str = Field(max_length=200, index=True)
    slug: str = Field(max_length=100, index=True)

    # Perfil público
    bio: Optional[str] = Field(default=None, max_length=3000)
    nacionalidad: Optional[str] = Field(default=None, max_length=100)
    anio_nacimiento: Optional[int] = Field(default=None)
    foto_perfil: Optional[str] = Field(default=None, max_length=500)
    sitio_web: Optional[str] = Field(default=None, max_length=500)
    cv_url: Optional[str] = Field(default=None, max_length=500)  # PDF descargable

    # Estado (soft delete, mismo patrón que el resto del sistema)
    activo: bool = Field(default=True, index=True)

    # Timestamps
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)

    # Relaciones
    galeria: Optional["Galeria"] = Relationship(back_populates="artistas")
    obras: List["Obra"] = Relationship(back_populates="artista")