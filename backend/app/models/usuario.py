from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.galeria import Galeria

class RolUsuario(str, Enum):
    """Roles del sistema (matriz de permisos)."""
    ADMIN = "admin"        # Dueño/Admin de la galería
    CURADOR = "curador"    # CRUD obras + exposiciones
    ASESOR = "asesor"      # Ver inventario + registrar ventas
    ARTISTA = "artista"    # Sus obras y sus ventas
    VIEWER = "viewer"      # Solo lectura

class UsuarioBase(SQLModel):
    """
    Base para schemas (mantiene compatibilidad con app/schemas/usuario.py).
    El campo 'rol' se usa aquí solo para la interfaz de creación, 
    pero la lógica real de permisos vive en UserGalleryRole.
    """
    email: str = Field(index=True, unique=True, max_length=255)
    nombre: str = Field(max_length=100)
    rol: RolUsuario = Field(default=RolUsuario.VIEWER)

class UserAccount(UsuarioBase, table=True):
    """
    Identidad global del usuario. 
    Un solo email = una sola cuenta, sin importar en cuántas galerías participe.
    """
    __tablename__ = "user_accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str                      # NUNCA guardar password en claro
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    ultimo_login: Optional[datetime] = None
    
    # Galería en la que el usuario está trabajando actualmente (contexto de sesión)
    galeria_id_activa: Optional[int] = Field(default=None, foreign_key="galerias.id", index=True)

    # Relaciones
    galeria_roles: List["UserGalleryRole"] = Relationship(back_populates="user")
    galeria_activa: Optional["Galeria"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UserAccount.galeria_id_activa]"}
    )

class UserGalleryRole(SQLModel, table=True):
    """
    Tabla intermedia: Define qué rol tiene un UserAccount en una Galería específica.
    """
    __tablename__ = "user_galeria_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user_accounts.id", index=True)
    galeria_id: int = Field(foreign_key="galerias.id", index=True)
    rol: RolUsuario = Field(default=RolUsuario.VIEWER)
    fecha_asignacion: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    user: "UserAccount" = Relationship(back_populates="galeria_roles")
    galeria: "Galeria" = Relationship(back_populates="user_roles")

# Alias para mantener compatibilidad con imports antiguos (ej: from app.models.usuario import Usuario)
Usuario = UserAccount