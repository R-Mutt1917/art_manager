from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas.exposicion import ExposicionCreate, ExposicionRead, AsignarObraSchema
from app.models.usuario import RolUsuario
from app.models.galeria import Galeria  # ← NUEVO
from app.core.dependencies import require_role, get_current_galeria  # ← NUEVO import
from app.services.exposicion_service import ExposicionService

router = APIRouter(prefix="/exposiciones", tags=["Exposiciones"])

def get_expo_service(session: Session = Depends(get_session)) -> ExposicionService:
    return ExposicionService(session)

# ==========================================
# CREAR EXPOSICIÓN (ADMIN, CURADOR)
# ==========================================
@router.post(
    "/", 
    response_model=ExposicionRead, 
    status_code=201,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def crear_exposicion(
    expo_data: ExposicionCreate, 
    service: ExposicionService = Depends(get_expo_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Crea una nueva exposición."""
    return service.crear_exposicion(expo_data, galeria)

# ==========================================
# ASIGNAR OBRA (ADMIN, CURADOR)
# ==========================================
@router.post(
    "/{expo_id}/obras/{obra_id}", 
    status_code=201,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def asignar_obra(
    expo_id: int,
    obra_id: int,
    asignacion_data: AsignarObraSchema,
    service: ExposicionService = Depends(get_expo_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """
    Asigna una obra a una exposición. 
    VALIDA automáticamente que no haya superposición de fechas con otras exposiciones.
    """
    return service.asignar_obra_a_exposicion(expo_id, obra_id, asignacion_data, galeria)

# ==========================================
# CHECKLIST DE RETIRO (ADMIN, CURADOR)
# ==========================================
@router.get(
    "/{expo_id}/checklist", 
    response_model=List[dict],
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def generar_checklist_retiro(
    expo_id: int, 
    service: ExposicionService = Depends(get_expo_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Genera la lista de obras que deben ser retiradas al finalizar esta exposición."""
    return service.obtener_checklist_retiro(expo_id, galeria)