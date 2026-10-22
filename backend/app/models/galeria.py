from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class Galeria(SQLModel, table=True):
    """
    Galería de arte (tenant principal del sistema multi-tenant).
    Cada galería tiene su espacio aislado con sus propios artistas,
    obras, compradores, exposiciones y préstamos.
    """
    __tablename__ = "galerias"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Identificación
    nombre: str = Field(max_length=200, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)  # Para URLs: /galeria-sur
    
    # Perfil público
    bio: Optional[str] = Field(default=None, max_length=2000)
    ubicacion: Optional[str] = Field(default=None, max_length=200)  # "Buenos Aires, Argentina"
    sitio_web: Optional[str] = Field(default=None, max_length=500)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    
    # Estado
    activo: bool = Field(default=True, index=True)
    
    # Timestamps
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)