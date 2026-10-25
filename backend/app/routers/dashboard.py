from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardStats
from app.models.usuario import RolUsuario
from app.models.galeria import Galeria
from app.core.dependencies import require_role, get_current_galeria

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_dashboard_service(session: Session = Depends(get_session)) -> DashboardService:
    return DashboardService(session)

# ==========================================
# GET STATS (ADMIN, CURADOR, ASESOR)
# ==========================================
@router.get(
    "/stats", 
    response_model=DashboardStats,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR, RolUsuario.ASESOR))]
)
def obtener_estadisticas(
    service: DashboardService = Depends(get_dashboard_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Métricas agregadas SOLO de la galería del usuario autenticado."""
    return service.obtener_estadisticas(galeria)