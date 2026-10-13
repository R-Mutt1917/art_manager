from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date

class CompradorCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = Field(default=None, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=300)
    notas: Optional[str] = None

class CompradorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=300)
    notas: Optional[str] = None
    activo: Optional[bool] = None

class CompradorRead(BaseModel):
    id: int
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    notas: Optional[str]
    activo: bool
    
    model_config = {"from_attributes": True}

class CompradorConObrasRead(CompradorRead):
    """Schema extendido que incluye las obras compradas."""
    obras_compradas: Optional[List[dict]] = None

class VentaCreate(BaseModel):
    """Schema para registrar una nueva venta."""
    obra_id: int
    comprador_id: int
    fecha_venta: Optional[str] = Field(default=None, description="Formato: YYYY-MM-DD")