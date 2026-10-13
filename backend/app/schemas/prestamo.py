from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class PrestamoCreate(BaseModel):
    obra_id: int
    prestatario_nombre: str = Field(..., min_length=1, max_length=200)
    prestatario_contacto: Optional[str] = Field(default=None, max_length=200)
    fecha_prestamo: str = Field(..., description="Formato: YYYY-MM-DD")
    fecha_devolucion_esperada: str = Field(..., description="Formato: YYYY-MM-DD")
    motivo: Optional[str] = Field(default=None, max_length=500)

class PrestamoRead(BaseModel):
    id: int
    obra_id: int
    prestatario_nombre: str
    prestatario_contacto: Optional[str]
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date]
    estado: str
    motivo: Optional[str]
    
    model_config = {"from_attributes": True}

class DevolucionPrestamo(BaseModel):
    """Schema para registrar la devolución de una obra."""
    fecha_devolucion_real: str = Field(..., description="Formato: YYYY-MM-DD")
    estado_obra_tras_devolucion: str = Field(default="disponible", description="generalmente 'disponible'")