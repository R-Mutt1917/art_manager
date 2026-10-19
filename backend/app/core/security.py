from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


# ==========================================
# Passwords
# ==========================================

def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt + salt automático."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña en claro contra su hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ==========================================
# JWT
# ==========================================

def _create_token(subject: int, rol: str, token_type: str, expires: timedelta) -> str:
    now = datetime.utcnow()
    payload: dict[str, Any] = {
        "sub": str(subject),
        "rol": rol,
        "type": token_type,
        "iat": now,
        "exp": now + expires,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(usuario_id: int, rol: str) -> str:
    return _create_token(
        usuario_id, rol, "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(usuario_id: int, rol: str) -> str:
    return _create_token(
        usuario_id, rol, "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decodifica y valida firma + expiración. Lanza jwt.PyJWTError si es inválido."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])