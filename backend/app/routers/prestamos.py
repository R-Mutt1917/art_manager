from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas.prestamo import PrestamoCreate, PrestamoRead, DevolucionPrestamo
from app.models.usuario import RolUsuario
from app.models.galeria import Galeria
from app.core.dependencies import require_role, get_current_galeria
from app.services.prestamo_service import PrestamoService

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

def get_prestamo_service(session: Session = Depends(get_session)) -> PrestamoService:
    return PrestamoService(session)

# ==========================================
# CREAR PRÉSTAMO (solo ADMIN — acción sensible)
# ==========================================
@router.post(
    "/",
    response_model=PrestamoRead,
    status_code=201,
    dependencies=[Depends(require_role(RolUsuario.ADMIN))]
)
def crear_prestamo(
    prestamo_data: PrestamoCreate,
    service: PrestamoService = Depends(get_prestamo_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Registra un nuevo préstamo y cambia el estado de la obra a 'en_prestamo'."""
    return service.registrar_prestamo(prestamo_data, galeria)

# ==========================================
# REGISTRAR DEVOLUCIÓN (solo ADMIN)
# ==========================================
@router.post(
    "/{prestamo_id}/devolucion",
    response_model=dict,
    dependencies=[Depends(require_role(RolUsuario.ADMIN))]
)
def registrar_devolucion(
    prestamo_id: int,
    devolucion_data: DevolucionPrestamo,
    service: PrestamoService = Depends(get_prestamo_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Registra la devolución de la obra y la libera para estar disponible nuevamente."""
    return service.registrar_devolucion(prestamo_id, devolucion_data, galeria)

# ==========================================
# LISTAR ACTIVOS (ADMIN, CURADOR)
# ==========================================
@router.get(
    "/activos",
    response_model=List[PrestamoRead],
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def listar_prestamos_activos(
    service: PrestamoService = Depends(get_prestamo_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Lista las obras actualmente en préstamo DE LA GALERÍA del usuario."""
    return service.obtener_prestamos_activos(galeria)