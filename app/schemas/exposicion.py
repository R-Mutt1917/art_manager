from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ExposicionCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    lugar: str = Field(..., max_length=200)
    fecha_inicio: date
    fecha_fin: date
    descripcion: Optional[str] = None

class ExposicionRead(BaseModel):
    id: int
    nombre: str
    lugar: str
    fecha_inicio: date
    fecha_fin: date
    descripcion: Optional[str]
    activa: bool
    
    model_config = {"from_attributes": True}

class AsignarObraSchema(BaseModel):
    """Schema para asignar una obra a una exposición con su ubicación."""
    sala: Optional[str] = Field(default=None, max_length=50)
    pared: Optional[str] = Field(default=None, max_length=50)