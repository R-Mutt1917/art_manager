from typing import Optional, List, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from app.models.obra_exposicion import ObraExposicion

class Exposicion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=200)
    lugar: str = Field(max_length=200)
    fecha_inicio: date
    fecha_fin: date
    descripcion: Optional[str] = Field(default=None)
    activa: bool = Field(default=True)
    
    asignaciones: Mapped[List["ObraExposicion"]] = Relationship(back_populates="exposicion")