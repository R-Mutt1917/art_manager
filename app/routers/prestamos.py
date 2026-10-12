from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas.prestamo import PrestamoCreate, PrestamoRead, DevolucionPrestamo
from app.services.prestamo_service import PrestamoService

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

def get_prestamo_service(session: Session = Depends(get_session)) -> PrestamoService:
    return PrestamoService(session)

@router.post("/", response_model=PrestamoRead, status_code=201)
def crear_prestamo(
    prestamo_data: PrestamoCreate,
    service: PrestamoService = Depends(get_prestamo_service)
):
    """Registra un nuevo préstamo y cambia el estado de la obra a 'en_prestamo'."""
    return service.registrar_prestamo(prestamo_data)

@router.post("/{prestamo_id}/devolucion", response_model=dict)
def registrar_devolucion(
    prestamo_id: int,
    devolucion_data: DevolucionPrestamo,
    service: PrestamoService = Depends(get_prestamo_service)
):
    """Registra la devolución de la obra y la libera para estar disponible nuevamente."""
    return service.registrar_devolucion(prestamo_id, devolucion_data)

@router.get("/activos", response_model=List[PrestamoRead])
def listar_prestamos_activos(
    service: PrestamoService = Depends(get_prestamo_service)
):
    """Lista todas las obras que están actualmente en préstamo."""
    return service.obtener_prestamos_activos()