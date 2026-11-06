from pydantic import BaseModel, EmailStr, Field

class GaleriaRegisterRequest(BaseModel):
    """
    Request para registrar una nueva galería + su dueño en una sola operación.
    """
    # Datos de la galería
    nombre_galeria: str = Field(min_length=2, max_length=200)
    bio_galeria: str | None = Field(default=None, max_length=2000)
    ubicacion_galeria: str | None = Field(default=None, max_length=200)
    sitio_web_galeria: str | None = Field(default=None, max_length=500)

    # Datos del dueño (primer ADMIN de la galería)
    email_dueno: EmailStr
    nombre_dueno: str = Field(min_length=2, max_length=100)
    password_dueno: str = Field(min_length=8, max_length=100)

class GaleriaRegisterResponse(BaseModel):
    """Response exitoso con los datos de la galería y el token para autologin."""
    galeria_id: int
    galeria_nombre: str
    galeria_slug: str
    user_id: int
    user_email: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"