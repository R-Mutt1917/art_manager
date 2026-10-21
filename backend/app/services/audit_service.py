import json
from typing import Optional

from sqlmodel import Session

from app.models.audit_log import AuditLog, TipoEvento


class AuditService:
    """Registra eventos de auditoría de forma centralizada."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def registrar(
        self,
        tipo_evento: TipoEvento,
        usuario_id: Optional[int],
        usuario_email: str,
        descripcion: str,
        entidad_tipo: Optional[str] = None,
        entidad_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        """Crea un registro de auditoría."""
        log = AuditLog(
            tipo_evento=tipo_evento,
            usuario_id=usuario_id,
            usuario_email=usuario_email,
            descripcion=descripcion,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            ip_address=ip_address,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        self.session.add(log)
        # NOTA: no hacemos commit acá. Lo hace el servicio principal,
        # para garantizar atomicidad (si la acción falla, el log tampoco queda).
        return log