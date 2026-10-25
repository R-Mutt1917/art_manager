from typing import List, Optional

from pydantic import BaseModel


class ObraPublicRead(BaseModel):
    """
    Vista pública y velada de una obra.
    SIN precio, SIN notas internas.
    CON statement: el texto curatorial es parte de la obra pública.
    """
    id: int
    titulo: str
    anio: int
    estado: str
    imagen_url: Optional[str] = None
    tecnica_nombre: Optional[str] = None
    statement: Optional[str] = None  # ← DEBE EXISTIR ESTA LÍNEA

    model_config = {"from_attributes": True}


class ArtistaPublicRead(BaseModel):
    """Perfil público de un artista."""
    id: int
    nombre: str
    slug: str
    bio: Optional[str] = None
    nacionalidad: Optional[str] = None
    anio_nacimiento: Optional[int] = None
    foto_perfil: Optional[str] = None
    sitio_web: Optional[str] = None

    model_config = {"from_attributes": True}


class ArtistaDetallePublicRead(ArtistaPublicRead):
    """Perfil público del artista + sus obras veladas."""
    obras: List[ObraPublicRead] = []


class GaleriaPublicRead(BaseModel):
    """Perfil público de la galería con contadores."""
    id: int
    nombre: str
    slug: str
    bio: Optional[str] = None
    ubicacion: Optional[str] = None
    sitio_web: Optional[str] = None
    logo_url: Optional[str] = None
    total_artistas: int = 0
    total_obras: int = 0

    model_config = {"from_attributes": True}