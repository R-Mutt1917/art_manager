from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select

from app.database import get_session
from app.models.obra import Obra, EstadoObra
from app.schemas.obra import ObraCreate, ObraUpdate, ObraRead

# Importamos el Servicio de Obras y las funciones de Imágenes
from app.services.obra_service import ObraService
from app.services.image_service import guardar_imagen, eliminar_imagen

router = APIRouter(prefix="/obras", tags=["Obras"])

# Dependency para inyectar el servicio
def get_obra_service(session: Session = Depends(get_session)) -> ObraService:
    return ObraService(session)

# ==========================================
# 1. ENDPOINTS CRUD (Usando el Service)
# ==========================================

@router.post("/", response_model=ObraRead, status_code=201)
def crear_obra(obra_data: ObraCreate, service: ObraService = Depends(get_obra_service)):
    """Crea una nueva obra en el inventario."""
    return service.crear(obra_data)

@router.get("/", response_model=List[ObraRead])
def listar_obras(
    estado: Optional[EstadoObra] = Query(None, description="Filtrar por estado"),
    tecnica_id: Optional[int] = Query(None, description="Filtrar por ID de técnica"),
    service: ObraService = Depends(get_obra_service)
):
    """Lista todas las obras activas."""
    return service.obtener_todas(estado=estado, tecnica_id=tecnica_id)

@router.get("/{obra_id}", response_model=ObraRead)
def obtener_obra(obra_id: int, service: ObraService = Depends(get_obra_service)):
    """Obtiene una obra por su ID."""
    return service.obtener_por_id(obra_id)

@router.put("/{obra_id}", response_model=ObraRead)
def actualizar_obra(
    obra_id: int, 
    obra_data: ObraUpdate, 
    service: ObraService = Depends(get_obra_service)
):
    """Actualiza parcialmente los datos de una obra existente."""
    return service.actualizar(obra_id, obra_data)

@router.delete("/{obra_id}")
def eliminar_obra(obra_id: int, service: ObraService = Depends(get_obra_service)):
    """Soft delete: Marca la obra como inactiva sin borrarla de la BD."""
    return service.eliminar_logico(obra_id)

# ==========================================
# 2. ENDPOINTS DE GESTIÓN DE IMÁGENES
# ==========================================

@router.post("/{obra_id}/imagen", response_model=ObraRead)
def subir_imagen_obra(
    obra_id: int,
    file: UploadFile = File(..., description="Archivo de imagen (JPG, PNG, GIF, máx 5MB)"),
    session: Session = Depends(get_session),
    service: ObraService = Depends(get_obra_service)
):
    """
    Sube o reemplaza la imagen de una obra existente.
    Si ya tenía una imagen, la elimina del disco antes de guardar la nueva.
    """
    # 1. Verificar que la obra existe y está activa
    obra = service.obtener_por_id(obra_id)
    
    # 2. Si ya tenía una imagen, eliminarla del sistema de archivos
    if obra.imagen_url:
        eliminar_imagen(obra.imagen_url)
    
    # 3. Guardar la nueva imagen y obtener la URL pública
    imagen_url = guardar_imagen(file)
    
    # 4. Actualizar la obra con la nueva URL y timestamp
    obra.imagen_url = imagen_url
    obra.fecha_actualizacion = datetime.utcnow()
    
    session.add(obra)
    session.commit()
    session.refresh(obra)
    
    return obra

@router.delete("/{obra_id}/imagen")
def eliminar_imagen_de_obra(
    obra_id: int,
    session: Session = Depends(get_session),
    service: ObraService = Depends(get_obra_service)
):
    """
    Elimina únicamente la imagen asociada a una obra, pero conserva la obra.
    """
    # 1. Verificar que la obra existe y está activa
    obra = service.obtener_por_id(obra_id)
    
    # 2. Verificar si realmente tiene una imagen para borrar
    if not obra.imagen_url:
        raise HTTPException(
            status_code=404, 
            detail="Esta obra no tiene una imagen asociada para eliminar"
        )
    
    # 3. Guardar la URL temporalmente para borrar el archivo físico
    url_a_borrar = obra.imagen_url
    
    # 4. Eliminar el archivo del sistema de archivos (carpeta uploads)
    eliminar_imagen(url_a_borrar)
    
    # 5. Actualizar la base de datos: quitar la URL y actualizar fecha
    obra.imagen_url = None
    obra.fecha_actualizacion = datetime.utcnow()
    
    session.add(obra)
    session.commit()
    
    return {"mensaje": "Imagen eliminada exitosamente. La obra ahora no tiene foto."}