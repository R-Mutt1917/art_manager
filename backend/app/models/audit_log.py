from typing import Optional
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field


class TipoEvento(str, Enum):
    """Eventos auditables del sistema."""
    # Auth
    LOGIN_EXITOSO = "login_exitoso"
    LOGIN_FALLIDO = "login_fallido"
    REGISTRO = "registro"
    
    # Obras
    OBRA_CREADA = "obra_creada"
    OBRA_EDITADA = "obra_editada"
    OBRA_ELIMINADA = "obra_eliminada"
    
    # Ventas
    VENTA_REGISTRADA = "venta_registrada"
    
    # Préstamos
    PRESTAMO_CREADO = "prestamo_creado"
    PRESTAMO_DEVUELTO = "prestamo_devuelto"


class AuditLog(SQLModel, table=True):
    """Registro inmutable de eventos críticos del sistema."""
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Quién
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario_email: str = Field(max_length=255)  # denormalizado: sobrevive aunque el usuario se borre
    
    # Qué
    tipo_evento: TipoEvento = Field(index=True)
    entidad_tipo: Optional[str] = Field(default=None, max_length=50)  # "obra", "usuario", etc.
    entidad_id: Optional[int] = None
    descripcion: str = Field(max_length=500)
    
    # Contexto
    ip_address: Optional[str] = Field(default=None, max_length=45)
    metadata_json: Optional[str] = None  # JSON con datos extra
    
    # Cuándo
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)