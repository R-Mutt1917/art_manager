from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.dependencies import require_role
from app.database import get_session
from app.models.audit_log import AuditLog, TipoEvento
from app.models.usuario import RolUsuario

router = APIRouter(prefix="/audit", tags=["Auditoría"])


class AuditLogRead(BaseModel):
    id: int
    tipo_evento: TipoEvento
    usuario_email: str
    descripcion: str
    entidad_tipo: Optional[str] = None
    entidad_id: Optional[int] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


@router.get(
    "/logs",
    response_model=List[AuditLogRead],
    dependencies=[Depends(require_role(RolUsuario.ADMIN))],
)
def listar_logs(
    limit: int = Query(100, le=500),
    tipo_evento: Optional[TipoEvento] = None,
    session: Session = Depends(get_session),
):
    """Lista logs de auditoría (solo ADMIN)."""
    stmt = select(AuditLog).order_by(AuditLog.timestamp.desc())  # type: ignore[attr-defined]

    if tipo_evento:
        stmt = stmt.where(AuditLog.tipo_evento == tipo_evento)

    return session.exec(stmt.limit(limit)).all()