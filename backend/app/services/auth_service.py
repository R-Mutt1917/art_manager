from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.usuario import Usuario, RolUsuario
from app.schemas.auth import LoginRequest
from app.schemas.usuario import UsuarioCreate


class AuthService:
    """Lógica de negocio de autenticación."""

    def __init__(self, session: Session):
        self.session = session

    def registrar(self, data: UsuarioCreate) -> Usuario:
        existente = self.session.exec(
            select(Usuario).where(Usuario.email == data.email)
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail="El email ya está registrado")

        usuario = Usuario(
            email=data.email,
            nombre=data.nombre,
            rol=RolUsuario.VIEWER,   # Registro público siempre entra como VIEWER
            password_hash=hash_password(data.password),
        )
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    def login(self, data: LoginRequest) -> dict:
        usuario = self.session.exec(
            select(Usuario).where(Usuario.email == data.email)
        ).first()

        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        if not usuario.activo:
            raise HTTPException(status_code=403, detail="Usuario desactivado")

        usuario.ultimo_login = datetime.utcnow()
        self.session.add(usuario)
        self.session.commit()

        return {
            "access_token": create_access_token(usuario.id, usuario.rol.value),
            "refresh_token": create_refresh_token(usuario.id, usuario.rol.value),
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Tipo de token incorrecto")

        usuario = self.session.get(Usuario, int(payload["sub"]))
        if not usuario or not usuario.activo:
            raise HTTPException(status_code=401, detail="Usuario no válido")

        return {
            "access_token": create_access_token(usuario.id, usuario.rol.value),
            "refresh_token": create_refresh_token(usuario.id, usuario.rol.value),
            "token_type": "bearer",
        }