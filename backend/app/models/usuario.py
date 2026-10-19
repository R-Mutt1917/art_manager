from typing import Optional
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field


class RolUsuario(str, Enum):
    """Roles del sistema (matriz de permisos de la Fase 2)."""
    ADMIN = "admin"        # Todo
    CURADOR = "curador"    # CRUD obras + exposiciones
    ASESOR = "asesor"      # Ver inventario + registrar ventas
    ARTISTA = "artista"    # Sus obras y sus ventas
    VIEWER = "viewer"      # Solo lectura


class UsuarioBase(SQLModel):
    email: str = Field(index=True, unique=True, max_length=255)
    nombre: str = Field(max_length=100)
    rol: RolUsuario = Field(default=RolUsuario.VIEWER)


class Usuario(UsuarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str                      # NUNCA guardar password en claro
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    ultimo_login: Optional[datetime] = None