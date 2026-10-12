from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.obra import EstadoObra

class ObraCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    anio: int = Field(..., ge=1000, le=9999)
    dimensiones: str = Field(..., max_length=50)
    precio: Optional[float] = Field(default=None, ge=0)
    estado: EstadoObra = Field(default=EstadoObra.DISPONIBLE)
    notas: Optional[str] = None
    tecnica_id: Optional[int] = None
    comprador_id: Optional[int] = None
    fecha_venta: Optional[date] = None

class ObraUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    anio: Optional[int] = Field(None, ge=1000, le=9999)
    dimensiones: Optional[str] = Field(None, max_length=50)
    precio: Optional[float] = Field(None, ge=0)
    estado: Optional[EstadoObra] = None
    notas: Optional[str] = None
    tecnica_id: Optional[int] = None
    comprador_id: Optional[int] = None
    fecha_venta: Optional[date] = None

class ObraRead(BaseModel):
    id: int
    titulo: str
    anio: int
    dimensiones: str
    precio: Optional[float]
    estado: EstadoObra
    imagen_url: Optional[str] = None # Campo opcional para la URL de la imagen
    notas: Optional[str]
    fecha_venta: Optional[date]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    tecnica_id: Optional[int]
    comprador_id: Optional[int]
    
    model_config = {"from_attributes": True} # Permite convertir SQLModel a Pydantic