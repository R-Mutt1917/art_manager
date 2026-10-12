from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

class Prestamo(SQLModel, table=True):
    """Registro de préstamo de una obra."""
    id: Optional[int] = Field(default=None, primary_key=True)
    obra_id: int = Field(foreign_key="obra.id", unique=True, description="La obra prestada")
    prestatario_nombre: str = Field(max_length=200)
    prestatario_contacto: Optional[str] = Field(default=None, max_length=200)
    fecha_prestamo: date = Field(description="Fecha de salida")
    fecha_devolucion_esperada: date = Field(description="Fecha límite de retorno")
    fecha_devolucion_real: Optional[date] = Field(default=None)
    motivo: Optional[str] = Field(default=None, max_length=500)
    
    # Relación 1:1
    obra: Optional["Obra"] = Relationship(back_populates="prestamo")