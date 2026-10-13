from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas.tecnica import TecnicaCreate, TecnicaRead
from app.services.tecnica_service import crear_tecnica as service_crear, obtener_todas_las_tecnicas as service_listar

router = APIRouter(prefix="/tecnicas", tags=["Técnicas"])

@router.post("/", response_model=TecnicaRead, status_code=201)
def crear_tecnica(tecnica_data: TecnicaCreate, session: Session = Depends(get_session)):
    """El router solo delega al service."""
    try:
        return service_crear(session, tecnica_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TecnicaRead])
def listar_tecnicas(session: Session = Depends(get_session)):
    """El router solo delega al service."""
    return service_listar(session)