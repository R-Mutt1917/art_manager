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
from app.models.usuario import UserAccount, UserGalleryRole, RolUsuario
from app.models.audit_log import TipoEvento
from app.schemas.auth import LoginRequest
from app.schemas.usuario import UsuarioCreate
from app.services.audit_service import AuditService

class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.audit = AuditService(session)

    def rol_efectivo(self, usuario: UserAccount) -> str:
        """
        Devuelve el rol REAL del usuario en su galería activa.
        ÚNICA fuente de verdad: UserGalleryRole.
        Si el usuario no tiene galería activa o no tiene rol asignado,
        devuelve VIEWER por defecto (seguridad por defecto).
        """
        if usuario.galeria_id_activa is not None:
            rol = self.session.exec(
                select(UserGalleryRole.rol).where(
                    UserGalleryRole.user_id == usuario.id,
                    UserGalleryRole.galeria_id == usuario.galeria_id_activa,
                )
            ).first()
            if rol is not None:
                return rol.value if hasattr(rol, "value") else str(rol)
        # Fallback seguro: sin rol asignado = VIEWER
        return RolUsuario.VIEWER.value

    def registrar(self, data: UsuarioCreate, request: Optional[Request] = None) -> UserAccount:
        """
        Registro público: crea una cuenta sin roles asignados.
        Los roles se asignan después, al vincular el usuario a una galería
        (vía onboarding self-service o por acción de un admin).
        """
        existente = self.session.exec(
            select(UserAccount).where(UserAccount.email == data.email)
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail="El email ya está registrado")

        usuario = UserAccount(
            email=data.email,
            nombre=data.nombre,
            password_hash=hash_password(data.password),
        )
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)

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
            select(UserAccount).where(UserAccount.email == data.email)
        ).first()

        if not usuario or not verify_password(data.password, usuario.password_hash):
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

        self.audit.registrar(
            tipo_evento=TipoEvento.LOGIN_EXITOSO,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            descripcion=f"Login exitoso: {usuario.email}",
            ip_address=request.client.host if request and request.client else None,
        )
        self.session.commit()

        rol = self.rol_efectivo(usuario)

        return {
            "access_token": create_access_token(usuario.id, rol),
            "refresh_token": create_refresh_token(usuario.id, rol),
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Tipo de token incorrecto")

        usuario = self.session.get(UserAccount, int(payload["sub"]))
        if not usuario or not usuario.activo:
            raise HTTPException(status_code=401, detail="Usuario no válido")

        rol = self.rol_efectivo(usuario)

        return {
            "access_token": create_access_token(usuario.id, rol),
            "refresh_token": create_refresh_token(usuario.id, rol),
            "token_type": "bearer",
        }