from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.core.security import decode_token
from app.database import get_session
from app.models.usuario import UserAccount, UserGalleryRole, RolUsuario
from app.models.galeria import Galeria

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> UserAccount:
    """
    Valida el Bearer token y retorna la cuenta de usuario (identidad global).
    """
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token incorrecto",
        )

    user_id = int(payload["sub"])
    user = session.get(UserAccount, user_id)

    if not user or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta de usuario no válida o inactiva",
        )

    return user

def get_current_galeria(
    user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Galeria:
    """
    Devuelve la galería (tenant) en la que el usuario está operando actualmente.
    Se basa en la 'galeria_id_activa' de la cuenta del usuario.
    """
    if user.galeria_id_activa is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes una galería activa asignada. Contactá al administrador.",
        )
    
    galeria = session.get(Galeria, user.galeria_id_activa)
    if not galeria or not galeria.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu galería activa no está disponible.",
        )
    
    return galeria

def require_role(*roles_permitidos: RolUsuario):
    """
    Factory que verifica si el usuario tiene uno de los roles permitidos 
    EN LA GALERÍA ACTIVA.
    """
    def role_checker(
        user: UserAccount = Depends(get_current_user),
        galeria: Galeria = Depends(get_current_galeria),
        session: Session = Depends(get_session)
    ) -> UserAccount:
        # Buscamos si existe un registro de rol para ESTE usuario en ESTA galería
        stmt = select(UserGalleryRole).where(
            UserGalleryRole.user_id == user.id,
            UserGalleryRole.galeria_id == galeria.id,
            UserGalleryRole.rol.in_(roles_permitidos)
        )
        role_assignment = session.exec(stmt).first()
        
        if not role_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos ({[r.value for r in roles_permitidos]}) en esta galería.",
            )
        return user

    return role_checker