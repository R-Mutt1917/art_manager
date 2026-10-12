from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

class Exposicion(SQLModel, table=True):
    """Muestra o evento donde se presentan las obras."""
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=200)
    lugar: str = Field(max_length=200)
    fecha_inicio: date
    fecha_fin: date
    descripcion: Optional[str] = Field(default=None)
    activa: bool = Field(default=True) # Por si queremos dar de baja una expo
    
    # Relación N:M: Una exposición tiene muchas relaciones con obras
    obras_en_exposicion: List["ObraExposicion"] = Relationship(back_populates="exposicion")