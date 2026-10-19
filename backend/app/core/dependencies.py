from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.core.security import decode_token
from app.database import get_session
from app.models.usuario import Usuario, RolUsuario

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Valida el Bearer token y retorna el usuario autenticado.
    Lanza 401 si el token es inválido, expirado o el usuario no existe.
    """
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    # Verificar que sea un access token (no refresh)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token incorrecto",
        )

    usuario_id = int(payload["sub"])
    usuario = session.get(Usuario, usuario_id)

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido",
        )

    return usuario


def require_role(*roles_permitidos: RolUsuario):
    """
    Factory que retorna una dependencia que verifica el rol del usuario.
    
    Uso:
        @router.post("/", dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))])
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {[r.value for r in roles_permitidos]}",
            )
        return current_user

    return role_checker