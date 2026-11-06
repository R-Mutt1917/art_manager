from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.galeria import Galeria

class RolUsuario(str, Enum):
    """Roles del sistema (matriz de permisos por galería)."""
    ADMIN = "admin"
    CURADOR = "curador"
    ASESOR = "asesor"
    ARTISTA = "artista"
    VIEWER = "viewer"

class UsuarioBase(SQLModel):
    """
    Base compartida para schemas.
    NOTA: NO incluye 'rol' — los roles se definen por galería en UserGalleryRole.
    """
    email: str = Field(index=True, unique=True, max_length=255)
    nombre: str = Field(max_length=100)

class UserAccount(UsuarioBase, table=True):
    """
    Identidad global del usuario.
    Un solo email = una sola cuenta, sin importar en cuántas galerías participe.
    Los roles del usuario viven en UserGalleryRole (relación muchos-a-muchos con Galeria).
    """
    __tablename__ = "user_accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
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
    Esta es la ÚNICA fuente de verdad de permisos del sistema.
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

# Alias de compatibilidad
Usuario = UserAccount