from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional

from app.database import get_session
from app.schemas.comprador import (
    CompradorCreate,
    CompradorUpdate,
    CompradorRead,
    CompradorConObrasRead,
    VentaCreate
)
from app.models.usuario import RolUsuario
from app.models.galeria import Galeria
from app.core.dependencies import require_role, get_current_galeria
from app.services.comprador_service import CompradorService

router = APIRouter(prefix="/compradores", tags=["Compradores"])

def get_comprador_service(session: Session = Depends(get_session)) -> CompradorService:
    return CompradorService(session)

# ==========================================
# CREATE (ADMIN, ASESOR)
# ==========================================
@router.post(
    "/",
    response_model=CompradorRead,
    status_code=201,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.ASESOR))]
)
def crear_comprador(
    comprador_data: CompradorCreate,
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """Crea un nuevo comprador en la galería del usuario autenticado."""
    return service.crear_comprador(comprador_data, galeria)

# ==========================================
# READ (listar)
# ==========================================
@router.get(
    "/",
    response_model=List[CompradorRead],
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.ASESOR, RolUsuario.CURADOR))]
)
def listar_compradores(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """Lista compradores DE LA GALERÍA del usuario autenticado."""
    return service.obtener_todos(galeria, activo=activo)

@router.get(
    "/{comprador_id}",
    response_model=CompradorConObrasRead,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.ASESOR, RolUsuario.CURADOR))]
)
def obtener_comprador(
    comprador_id: int,
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """Obtiene un comprador y su historial de compras (con aislamiento)."""
    comprador = service.obtener_por_id(comprador_id, galeria)
    obras = service.obtener_historial_compras(comprador_id, galeria)

    return {
        "id": comprador.id,
        "nombre": comprador.nombre,
        "email": comprador.email,
        "telefono": comprador.telefono,
        "direccion": comprador.direccion,
        "notas": comprador.notas,
        "activo": comprador.activo,
        "obras_compradas": obras
    }

@router.get(
    "/{comprador_id}/compras",
    response_model=List[dict],
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.ASESOR, RolUsuario.CURADOR))]
)
def historial_de_compras(
    comprador_id: int,
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """Obtiene el historial completo de compras de un comprador (con aislamiento)."""
    return service.obtener_historial_compras(comprador_id, galeria)

# ==========================================
# UPDATE (ADMIN, ASESOR)
# ==========================================
@router.put(
    "/{comprador_id}",
    response_model=CompradorRead,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.ASESOR))]
)
def actualizar_comprador(
    comprador_id: int,
    comprador_data: CompradorUpdate,
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """Actualiza los datos de un comprador con aislamiento."""
    return service.actualizar_comprador(comprador_id, comprador_data, galeria)

# ==========================================
# DELETE (solo ADMIN — acción destructiva)
# ==========================================
@router.delete(
    "/{comprador_id}",
    dependencies=[Depends(require_role(RolUsuario.ADMIN))]
)
def eliminar_comprador(
    comprador_id: int,
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """Soft delete de un comprador con aislamiento."""
    return service.eliminar_logico(comprador_id, galeria)

# ==========================================
# REGISTRAR VENTA (ADMIN, ASESOR)
# ==========================================
@router.post(
    "/ventas/registrar",
    status_code=201,
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.ASESOR))]
)
def registrar_venta(
    venta_data: VentaCreate,
    service: CompradorService = Depends(get_comprador_service),
    galeria: Galeria = Depends(get_current_galeria),
):
    """
    Registra la venta de una obra a un comprador.
    Con aislamiento: valida que obra y comprador pertenecen a la galería.
    """
    return service.registrar_venta(
        obra_id=venta_data.obra_id,
        comprador_id=venta_data.comprador_id,
        galeria=galeria,
        fecha_venta=venta_data.fecha_venta
    )