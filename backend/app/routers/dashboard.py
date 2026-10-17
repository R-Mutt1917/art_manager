from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardStats  # ← NUEVO

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(session: Session = Depends(get_session)) -> DashboardService:
    return DashboardService(session)


@router.get("/stats", response_model=DashboardStats)  # ← response_model
def obtener_estadisticas(
    service: DashboardService = Depends(get_dashboard_service)
):
    return service.obtener_estadisticas()