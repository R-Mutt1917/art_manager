from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UsuarioCreate(BaseModel):
    """Registro público: solo identidad + password. Sin rol (se asigna por galería)."""
    email: EmailStr
    nombre: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=100)

class UsuarioRead(BaseModel):
    """
    Vista pública del usuario.
    El rol NO se expone aquí porque depende de la galería activa (se obtiene vía /auth/me).
    """
    id: int
    email: str
    nombre: str
    activo: bool
    fecha_creacion: datetime
    galeria_id_activa: int | None = None

    model_config = {"from_attributes": True}