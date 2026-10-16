from typing import Optional
from pydantic import Field
from app.models.tecnica import TecnicaBase

class TecnicaCreate(TecnicaBase):
    """Schema para CREAR una nueva técnica (todos los campos obligatorios según TecnicaBase)."""
    pass

class TecnicaUpdate(TecnicaBase):
    """
    Schema para ACTUALIZAR una técnica.
    Todos los campos son opcionales (permite actualización parcial).
    """
    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)

class TecnicaRead(TecnicaBase):
    """Schema para LEER una técnica (incluye el ID generado por la BD)."""
    id: int
    
    model_config = {"from_attributes": True}