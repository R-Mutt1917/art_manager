from datetime import datetime
from typing import List, Optional
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlmodel import Session, select

from app.database import get_session
from app.models.obra import Obra, EstadoObra
from app.models.tecnica import Tecnica
from app.models.usuario import Usuario, RolUsuario
from app.models.galeria import Galeria
from app.schemas.obra import ObraCreate, ObraUpdate, ObraRead
from app.services.obra_service import ObraService
from app.services.image_service import guardar_imagen, eliminar_imagen
from app.core.dependencies import require_role, get_current_galeria

router = APIRouter(prefix="/obras", tags=["Obras"])

def get_obra_service(session: Session = Depends(get_session)) -> ObraService:
    return ObraService(session)

# ==========================================
# CREATE
# ==========================================

@router.post(
        "/", 
        response_model=ObraRead, 
        status_code=201,
        dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def crear_obra(
    titulo: str = Form(...),
    anio: int = Form(...),
    dimensiones: str = Form(...),
    precio: Optional[float] = Form(None),
    estado: str = Form("disponible"),
    notas: Optional[str] = Form(None),
    statement: Optional[str] = Form(None),
    tecnica: str = Form(...),
    imagen: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    service: ObraService = Depends(get_obra_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Crea una obra en la galería del usuario autenticado."""
    
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
    
    # 3. Crear la obra (asignada a la galería del usuario)
    try:
        estado_enum = EstadoObra(estado)
    except ValueError:
        estado_enum = EstadoObra.DISPONIBLE

    obra_data = ObraCreate(
        titulo=titulo,
        anio=anio,
        dimensiones=dimensiones,
        precio=precio,
        estado=estado_enum,
        notas=notas,
        statement=statement,
        tecnica_id=tecnica_obj.id,
        imagen_url=imagen_url
    )
    
    return service.crear(obra_data, galeria)  # ← NUEVO: pasar galería

# ==========================================
# READ (con filtros) — filtrado por galería
# ==========================================

@router.get("/", response_model=List[ObraRead])
def listar_obras(
    estado: Optional[EstadoObra] = Query(None, description="Filtrar por estado"),
    tecnica_id: Optional[int] = Query(None, description="Filtrar por ID de técnica"),
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    busqueda: Optional[str] = Query(None, description="Buscar en título o notas"),
    service: ObraService = Depends(get_obra_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Lista obras DE LA GALERÍA del usuario autenticado."""
    return service.obtener_todas(
        galeria=galeria,
        estado=estado, 
        tecnica_id=tecnica_id,
        precio_min=precio_min,
        precio_max=precio_max,
        busqueda=busqueda
    )

# ==========================================
# PUBLIC CATALOG (sin datos sensibles, sin auth)
# ==========================================

@router.get("/publicas", response_model=List[dict])
def listar_obras_publicas(
    estado: Optional[EstadoObra] = Query(None, description="Filtrar por estado"),
    tecnica_id: Optional[int] = Query(None, description="Filtrar por ID de técnica"),
    busqueda: Optional[str] = Query(None, description="Buscar en título"),
    session: Session = Depends(get_session),
):
    """
    Catálogo público velado (no requiere auth, ve todas las galerías).
    Muestra datos básicos + imagen con blur.
    """
    # Query sin filtro de galería (público ve todo)
    query = select(Obra).where(Obra.activo == True)
    
    if estado:
        query = query.where(Obra.estado == estado)
    if tecnica_id:
        query = query.where(Obra.tecnica_id == tecnica_id)
    if busqueda:
        termino = f"%{busqueda.lower()}%"
        query = query.where(
            (Obra.titulo.ilike(termino)) | (Obra.notas.ilike(termino))
        )
    
    obras = session.exec(query).all()
    
    obras_publicas = []
    for obra in obras:
        obras_publicas.append({
            "id": obra.id,
            "titulo": obra.titulo,
            "anio": obra.anio,
            "tecnica_id": obra.tecnica_id,
            "estado": obra.estado.value if hasattr(obra.estado, 'value') else str(obra.estado),
            "imagen_url": obra.imagen_url,
        })
    
    return obras_publicas

@router.get("/{obra_id}", response_model=ObraRead)
def obtener_obra(
    obra_id: int,
    service: ObraService = Depends(get_obra_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    return service.obtener_por_id(obra_id, galeria)

# ==========================================
# UPDATE (acepta FormData)
# ==========================================

@router.put(
        "/{obra_id}", 
        response_model=ObraRead,
        dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def actualizar_obra(
    obra_id: int,
    titulo: str = Form(...),
    anio: int = Form(...),
    dimensiones: str = Form(...),
    precio: Optional[float] = Form(None),
    estado: str = Form("disponible"),
    notas: Optional[str] = Form(None),
    statement: Optional[str] = Form(None),
    tecnica: str = Form(...),
    imagen: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    service: ObraService = Depends(get_obra_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Actualiza una obra (con aislamiento por galería)."""
    # 1. Verificar que la obra existe Y pertenece a esta galería
    obra_existente = service.obtener_por_id(obra_id, galeria)
    
    # 2. Resolver técnica (upsert)
    tecnica_obj = session.exec(select(Tecnica).where(Tecnica.nombre == tecnica)).first()
    if not tecnica_obj:
        tecnica_obj = Tecnica(nombre=tecnica, descripcion="Creada desde edición")
        session.add(tecnica_obj)
        session.commit()
        session.refresh(tecnica_obj)
    
    # 3. Procesar imagen nueva si viene
    datos_update = {
        "titulo": titulo,
        "anio": anio,
        "dimensiones": dimensiones,
        "precio": precio,
        "notas": notas,
        "statement": statement,
        "tecnica_id": tecnica_obj.id,
    }
    
    try:
        datos_update["estado"] = EstadoObra(estado)
    except ValueError:
        datos_update["estado"] = EstadoObra.DISPONIBLE
    
    if imagen and imagen.filename:
        if obra_existente.imagen_url:
            eliminar_imagen(obra_existente.imagen_url)
        
        try:
            datos_update["imagen_url"] = guardar_imagen(imagen)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")
    
    # 4. Aplicar la actualización
    obra_update = ObraUpdate(**datos_update)
    return service.actualizar(obra_id, obra_update, galeria)  # ← NUEVO

# ==========================================
# DELETE (Soft delete)
# ==========================================

@router.delete(
    "/{obra_id}",
    dependencies=[Depends(require_role(RolUsuario.ADMIN, RolUsuario.CURADOR))]
)
def eliminar_obra(
    obra_id: int,
    service: ObraService = Depends(get_obra_service),
    galeria: Galeria = Depends(get_current_galeria),  # ← NUEVO
):
    """Soft delete con aislamiento."""
    return service.eliminar_logico(obra_id, galeria)