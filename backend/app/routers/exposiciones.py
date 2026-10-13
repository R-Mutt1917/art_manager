from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas.exposicion import ExposicionCreate, ExposicionRead, AsignarObraSchema
from app.services.exposicion_service import ExposicionService

router = APIRouter(prefix="/exposiciones", tags=["Exposiciones"])

def get_expo_service(session: Session = Depends(get_session)) -> ExposicionService:
    return ExposicionService(session)

@router.post("/", response_model=ExposicionRead, status_code=201)
def crear_exposicion(expo_data: ExposicionCreate, service: ExposicionService = Depends(get_expo_service)):
    """Crea una nueva exposición."""
    return service.crear_exposicion(expo_data)

@router.post("/{expo_id}/obras/{obra_id}", status_code=201)
def asignar_obra(
    expo_id: int,
    obra_id: int,
    asignacion_data: AsignarObraSchema,
    service: ExposicionService = Depends(get_expo_service)
):
    """
    Asigna una obra a una exposición. 
    VALIDA automáticamente que no haya superposición de fechas con otras exposiciones.
    """
    return service.asignar_obra_a_exposicion(expo_id, obra_id, asignacion_data)

@router.get("/{expo_id}/checklist", response_model=List[dict])
def generar_checklist_retiro(expo_id: int, service: ExposicionService = Depends(get_expo_service)):
    """
    Genera la lista de obras que deben ser retiradas al finalizar esta exposición.
    """
    return service.obtener_checklist_retiro(expo_id)