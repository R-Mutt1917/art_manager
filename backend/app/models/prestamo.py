from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from app.models.obra import Obra

class Prestamo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    obra_id: int = Field(foreign_key="obra.id", unique=True)
    prestatario_nombre: str = Field(max_length=200)
    prestatario_contacto: Optional[str] = Field(default=None, max_length=200)
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date] = Field(default=None)
    estado: str = Field(default="activo", max_length=20)
    motivo: Optional[str] = Field(default=None, max_length=500)
    
    obra: Mapped[Optional["Obra"]] = Relationship(back_populates="prestamo")