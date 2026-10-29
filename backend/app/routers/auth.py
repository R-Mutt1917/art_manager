from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.database import get_session
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.galeria import Galeria
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)


@router.post("/register", response_model=UsuarioRead, status_code=201)
def register(
    data: UsuarioCreate,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    """Registro público. El rol siempre entra como VIEWER (seguridad por defecto)."""
    return service.registrar(data, request)


@router.post("/login", response_model=TokenPair)
def login(
    data: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    """Valida credenciales y devuelve access + refresh tokens con el rol efectivo."""
    return service.login(data, request)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    """Canjea un refresh token válido por un nuevo par de tokens."""
    return service.refresh(data.refresh_token)


@router.get("/me")
def me(
    usuario: Usuario = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
):
    """
    Devuelve la identidad + rol EFECTIVO + galería activa del token actual.
    Lo usa el frontend (HeaderNav y gates SSR de páginas privadas).
    """
    galeria = None
    if usuario.galeria_id_activa is not None:
        galeria = session.get(Galeria, usuario.galeria_id_activa)

    return {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "rol": service.rol_efectivo(usuario),
        "galeria_id": usuario.galeria_id_activa,
        "galeria_nombre": galeria.nombre if galeria else None,
        "galeria_slug": galeria.slug if galeria else None,
    }