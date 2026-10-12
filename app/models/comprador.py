from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING  # ← IMPORTANTE: TYPE_CHECKING va aquí
from sqlmodel import SQLModel, Field, Relationship

# Esto solo se ejecuta cuando Pylance/MyPy analiza el código, NO en runtime
if TYPE_CHECKING:
    from app.models.obra import Obra

class Comprador(SQLModel, table=True):
    """Persona o entidad que adquiere obras de arte."""
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=200)
    email: Optional[str] = Field(default=None, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=300)
    notas: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)
    
    # Pylance ahora sabe que "Obra" existe gracias a TYPE_CHECKING
    obras: List["Obra"] = Relationship(back_populates="comprador")