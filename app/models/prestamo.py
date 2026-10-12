from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.obra import Obra

class Prestamo(SQLModel, table=True):
    """Registro de préstamo temporal de una obra."""
    id: Optional[int] = Field(default=None, primary_key=True)
    obra_id: int = Field(foreign_key="obra.id", unique=True, index=True)
    prestatario_nombre: str = Field(max_length=200, description="Nombre de quien recibe la obra")
    prestatario_contacto: Optional[str] = Field(default=None, max_length=200)
    fecha_prestamo: date = Field(description="Fecha de salida de la obra")
    fecha_devolucion_esperada: date = Field(description="Fecha límite de retorno")
    fecha_devolucion_real: Optional[date] = Field(default=None, description="Fecha en que se devolvió realmente")
    estado: str = Field(default="activo", max_length=20, description="activo, devuelto, vencido")
    motivo: Optional[str] = Field(default=None, max_length=500)
    
    # Relación 1:1
    obra: Optional["Obra"] = Relationship(back_populates="prestamo")