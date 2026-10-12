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
from app.services.comprador_service import CompradorService

router = APIRouter(prefix="/compradores", tags=["Compradores"])

def get_comprador_service(session: Session = Depends(get_session)) -> CompradorService:
    return CompradorService(session)

@router.post("/", response_model=CompradorRead, status_code=201)
def crear_comprador(
    comprador_data: CompradorCreate,
    service: CompradorService = Depends(get_comprador_service)
):
    """Crea un nuevo comprador."""
    return service.crear_comprador(comprador_data)

@router.get("/", response_model=List[CompradorRead])
def listar_compradores(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: CompradorService = Depends(get_comprador_service)
):
    """Lista todos los compradores."""
    return service.obtener_todos(activo=activo)

@router.get("/{comprador_id}", response_model=CompradorConObrasRead)
def obtener_comprador(
    comprador_id: int,
    service: CompradorService = Depends(get_comprador_service)
):
    """Obtiene un comprador y su historial de compras."""
    comprador = service.obtener_por_id(comprador_id)
    obras = service.obtener_historial_compras(comprador_id)
    
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

@router.put("/{comprador_id}", response_model=CompradorRead)
def actualizar_comprador(
    comprador_id: int,
    comprador_data: CompradorUpdate,
    service: CompradorService = Depends(get_comprador_service)
):
    """Actualiza los datos de un comprador."""
    return service.actualizar_comprador(comprador_id, comprador_data)

@router.delete("/{comprador_id}")
def eliminar_comprador(
    comprador_id: int,
    service: CompradorService = Depends(get_comprador_service)
):
    """Soft delete de un comprador (solo si no tiene obras asociadas)."""
    return service.eliminar_logico(comprador_id)

@router.get("/{comprador_id}/compras", response_model=List[dict])
def historial_de_compras(
    comprador_id: int,
    service: CompradorService = Depends(get_comprador_service)
):
    """Obtiene el historial completo de compras de un comprador."""
    return service.obtener_historial_compras(comprador_id)

@router.post("/ventas/registrar", status_code=201)
def registrar_venta(
    venta_data: VentaCreate,
    service: CompradorService = Depends(get_comprador_service)
):
    """
    Registra la venta de una obra a un comprador.
    Actualiza automáticamente el estado de la obra a 'vendida'.
    """
    return service.registrar_venta(
        obra_id=venta_data.obra_id,
        comprador_id=venta_data.comprador_id,
        fecha_venta=venta_data.fecha_venta
    )