from datetime import datetime
from typing import Optional

from fastapi import HTTPException, Request
from sqlmodel import Session, select

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.usuario import Usuario, RolUsuario
from app.models.audit_log import TipoEvento
from app.schemas.auth import LoginRequest
from app.schemas.usuario import UsuarioCreate
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.audit = AuditService(session)

    def registrar(self, data: UsuarioCreate, request: Optional[Request] = None) -> Usuario:
        existente = self.session.exec(
            select(Usuario).where(Usuario.email == data.email)
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail="El email ya está registrado")

        usuario = Usuario(
            email=data.email,
            nombre=data.nombre,
            rol=RolUsuario.VIEWER,
            password_hash=hash_password(data.password),
        )
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)

        # Auditoría: nuevo registro
        self.audit.registrar(
            tipo_evento=TipoEvento.REGISTRO,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            descripcion=f"Nuevo usuario registrado: {usuario.email}",
            entidad_tipo="usuario",
            entidad_id=usuario.id,
            ip_address=request.client.host if request and request.client else None,
        )
        self.session.commit()

        return usuario

    def login(self, data: LoginRequest, request: Optional[Request] = None) -> dict:
        usuario = self.session.exec(
            select(Usuario).where(Usuario.email == data.email)
        ).first()

        if not usuario or not verify_password(data.password, usuario.password_hash):
            # Auditoría: intento fallido (clave para detectar ataques de fuerza bruta)
            self.audit.registrar(
                tipo_evento=TipoEvento.LOGIN_FALLIDO,
                usuario_id=usuario.id if usuario else None,
                usuario_email=data.email,
                descripcion=f"Intento de login fallido para: {data.email}",
                ip_address=request.client.host if request and request.client else None,
            )
            self.session.commit()
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not usuario.activo:
            raise HTTPException(status_code=403, detail="Usuario desactivado")

        usuario.ultimo_login = datetime.utcnow()
        self.session.add(usuario)

        # Auditoría: login exitoso
        self.audit.registrar(
            tipo_evento=TipoEvento.LOGIN_EXITOSO,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            descripcion=f"Login exitoso: {usuario.email}",
            ip_address=request.client.host if request and request.client else None,
        )
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