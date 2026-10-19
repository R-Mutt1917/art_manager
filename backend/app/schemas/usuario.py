from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.usuario import UsuarioBase


class UsuarioCreate(BaseModel):
    """Registro público: SIN rol (siempre entra como VIEWER por seguridad)."""
    email: EmailStr
    nombre: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=100)


class UsuarioRead(UsuarioBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    model_config = {"from_attributes": True}
    