from datetime import datetime
from typing import List, Optional
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlmodel import Session, select

from app.database import get_session
from app.models.obra import Obra, EstadoObra
from app.models.tecnica import Tecnica
from app.schemas.obra import ObraCreate, ObraUpdate, ObraRead
from app.services.obra_service import ObraService
from app.services.image_service import guardar_imagen

router = APIRouter(prefix="/obras", tags=["Obras"])

def get_obra_service(session: Session = Depends(get_session)) -> ObraService:
    return ObraService(session)

@router.post("/", response_model=ObraRead, status_code=201)
def crear_obra(
    titulo: str = Form(...),
    anio: int = Form(...),
    dimensiones: str = Form(...),
    precio: Optional[float] = Form(None),
    estado: str = Form("disponible"),
    notas: Optional[str] = Form(None),
    tecnica: str = Form(...),  # Nombre de la técnica (crea si no existe)
    imagen: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    service: ObraService = Depends(get_obra_service)
):
    """Crea una obra. Si la técnica no existe, la crea automáticamente."""
    
    # 1. Buscar o crear la técnica
    tecnica_obj = session.exec(select(Tecnica).where(Tecnica.nombre == tecnica)).first()
    
    if not tecnica_obj:
        # Crear nueva técnica
        tecnica_obj = Tecnica(nombre=tecnica, descripcion="Creada desde el formulario")
        session.add(tecnica_obj)
        session.commit()
        session.refresh(tecnica_obj)
    
    # 2. Procesar imagen si existe
    imagen_url = None
    if imagen and imagen.filename:
        try:
            imagen_url = guardar_imagen(imagen)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")
    
    # 3. Crear la obra
    try:
        estado_enum = EstadoObra(estado)
    except ValueError:
        estado_enum = EstadoObra.disponible

    obra_data = ObraCreate(
        titulo=titulo,
        anio=anio,
        dimensiones=dimensiones,
        precio=precio,
        estado=estado_enum,
        notas=notas,
        tecnica_id=tecnica_obj.id,
        imagen_url=imagen_url
    )
    
    return service.crear(obra_data)


@router.get("/", response_model=List[ObraRead])
def listar_obras(
    estado: Optional[EstadoObra] = Query(None),
    tecnica_id: Optional[int] = Query(None),
    service: ObraService = Depends(get_obra_service)
):
    return service.obtener_todas(estado=estado, tecnica_id=tecnica_id)


@router.get("/{obra_id}", response_model=ObraRead)
def obtener_obra(obra_id: int, service: ObraService = Depends(get_obra_service)):
    return service.obtener_por_id(obra_id)

@router.delete("/{obra_id}")
def eliminar_obra(obra_id: int, service: ObraService = Depends(get_obra_service)):
    """Soft delete: Marca la obra como inactiva sin borrarla de la BD."""
    return service.eliminar_logico(obra_id)