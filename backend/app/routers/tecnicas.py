from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.schemas.tecnica import TecnicaCreate, TecnicaRead, TecnicaUpdate
from app.models.tecnica import Tecnica
from app.models.obra import Obra
from app.services.tecnica_service import (
    crear_tecnica as service_crear, 
    obtener_todas_las_tecnicas as service_listar
)

router = APIRouter(prefix="/tecnicas", tags=["Técnicas"])

# ==========================================
# CREATE
# ==========================================

@router.post("/", response_model=TecnicaRead, status_code=201)
def crear_tecnica(tecnica_data: TecnicaCreate, session: Session = Depends(get_session)):
    """Crea una nueva técnica."""
    try:
        return service_crear(session, tecnica_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# READ
# ==========================================

@router.get("/", response_model=List[TecnicaRead])
def listar_tecnicas(session: Session = Depends(get_session)):
    """Lista todas las técnicas."""
    return service_listar(session)


@router.get("/{tecnica_id}", response_model=TecnicaRead)
def obtener_tecnica(tecnica_id: int, session: Session = Depends(get_session)):
    """Obtiene una técnica específica por su ID."""
    tecnica = session.get(Tecnica, tecnica_id)
    if not tecnica:
        raise HTTPException(status_code=404, detail="Técnica no encontrada")
    return tecnica


# ==========================================
# UPDATE
# ==========================================

@router.put("/{tecnica_id}", response_model=TecnicaRead)
def actualizar_tecnica(
    tecnica_id: int, 
    tecnica_data: TecnicaUpdate, 
    session: Session = Depends(get_session)
):
    """Actualiza una técnica existente."""
    tecnica = session.get(Tecnica, tecnica_id)
    if not tecnica:
        raise HTTPException(status_code=404, detail="Técnica no encontrada")
    
    # Actualizar solo campos proporcionados
    update_data = tecnica_data.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(tecnica, campo, valor)
        
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)
    return tecnica


# ==========================================
# DELETE (con validación de obras asociadas)
# ==========================================

@router.delete("/{tecnica_id}")
def eliminar_tecnica(tecnica_id: int, session: Session = Depends(get_session)):
    """
    Elimina una técnica SOLO si no tiene obras asociadas.
    """
    tecnica = session.get(Tecnica, tecnica_id)
    if not tecnica:
        raise HTTPException(status_code=404, detail="Técnica no encontrada")
    
    # VALIDACIÓN: Verificar si hay obras usando esta técnica
    obras_asociadas = session.exec(
        select(Obra).where(Obra.tecnica_id == tecnica_id)
    ).first()
    
    if obras_asociadas:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar '{tecnica.nombre}' porque tiene obras asociadas."
        )
    
    session.delete(tecnica)
    session.commit()
    return {"mensaje": f"Técnica '{tecnica.nombre}' eliminada exitosamente"}