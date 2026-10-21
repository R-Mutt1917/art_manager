from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.database import get_session
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
    """Valida credenciales y devuelve access + refresh tokens."""
    return service.login(data, request)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    """Canjea un refresh token válido por un nuevo par de tokens."""
    return service.refresh(data.refresh_token)