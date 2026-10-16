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
from app.services.image_service import guardar_imagen, eliminar_imagen

router = APIRouter(prefix="/obras", tags=["Obras"])

def get_obra_service(session: Session = Depends(get_session)) -> ObraService:
    return ObraService(session)


# ==========================================
# CREATE
# ==========================================

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


# ==========================================
# READ (con filtros avanzados)
# ==========================================

@router.get("/", response_model=List[ObraRead])
def listar_obras(
    estado: Optional[EstadoObra] = Query(None, description="Filtrar por estado"),
    tecnica_id: Optional[int] = Query(None, description="Filtrar por ID de técnica"),
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    busqueda: Optional[str] = Query(None, description="Buscar en título o notas"),
    service: ObraService = Depends(get_obra_service)
):
    """Lista obras con filtros avanzados."""
    return service.obtener_todas(
        estado=estado, 
        tecnica_id=tecnica_id,
        precio_min=precio_min,
        precio_max=precio_max,
        busqueda=busqueda
    )


@router.get("/{obra_id}", response_model=ObraRead)
def obtener_obra(obra_id: int, service: ObraService = Depends(get_obra_service)):
    return service.obtener_por_id(obra_id)


# ==========================================
# UPDATE (Camino A: acepta FormData)
# ==========================================

@router.put("/{obra_id}", response_model=ObraRead)
def actualizar_obra(
    obra_id: int,
    titulo: str = Form(...),
    anio: int = Form(...),
    dimensiones: str = Form(...),
    precio: Optional[float] = Form(None),
    estado: str = Form("disponible"),
    notas: Optional[str] = Form(None),
    tecnica: str = Form(...),
    imagen: Optional[UploadFile] = File(None),  # Nueva imagen opcional
    session: Session = Depends(get_session),
    service: ObraService = Depends(get_obra_service)
):
    """
    Actualiza una obra existente.
    Acepta FormData para permitir cambiar la imagen en la misma operación.
    Si no se envía imagen, conserva la actual.
    """
    # 1. Verificar que la obra existe (lanza 404 si no)
    obra_existente = service.obtener_por_id(obra_id)
    
    # 2. Resolver técnica (upsert, igual que en POST)
    tecnica_obj = session.exec(select(Tecnica).where(Tecnica.nombre == tecnica)).first()
    if not tecnica_obj:
        tecnica_obj = Tecnica(nombre=tecnica, descripcion="Creada desde edición")
        session.add(tecnica_obj)
        session.commit()
        session.refresh(tecnica_obj)
    
    # 3. Procesar imagen nueva si viene (reemplaza la anterior)
    datos_update = {
        "titulo": titulo,
        "anio": anio,
        "dimensiones": dimensiones,
        "precio": precio,
        "notas": notas,
        "tecnica_id": tecnica_obj.id,
    }
    
    try:
        datos_update["estado"] = EstadoObra(estado)
    except ValueError:
        datos_update["estado"] = EstadoObra.disponible
    
    if imagen and imagen.filename:
        # Borrar imagen anterior del disco si existía
        if obra_existente.imagen_url:
            eliminar_imagen(obra_existente.imagen_url)
        
        try:
            datos_update["imagen_url"] = guardar_imagen(imagen)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")
    # Si NO viene imagen, no tocamos imagen_url (se conserva la actual)
    
    # 4. Aplicar la actualización vía service
    obra_update = ObraUpdate(**datos_update)
    return service.actualizar(obra_id, obra_update)


# ==========================================
# DELETE (Soft delete)
# ==========================================

@router.delete("/{obra_id}")
def eliminar_obra(obra_id: int, service: ObraService = Depends(get_obra_service)):
    """Soft delete: Marca la obra como inactiva sin borrarla de la BD."""
    return service.eliminar_logico(obra_id)