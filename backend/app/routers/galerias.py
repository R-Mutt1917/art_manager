from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.database import get_session
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.obra import Obra
from app.models.tecnica import Tecnica
from app.schemas.public import (
    GaleriaPublicRead,
    ArtistaPublicRead,
    ArtistaDetallePublicRead,
    ObraPublicRead,
)
from app.schemas.galeria import GaleriaRegisterRequest, GaleriaRegisterResponse
from app.services.galeria_service import GaleriaService

router = APIRouter(prefix="/galerias", tags=["Galerías"])

# ==========================================
# HELPERS PRIVADOS
# ==========================================

def _obtener_galeria_activa_o_404(session: Session, slug: str) -> Galeria:
    """Resuelve la galería por slug. 404 si no existe o está inactiva."""
    galeria = session.exec(
        select(Galeria).where(Galeria.slug == slug, Galeria.activo == True)
    ).first()
    if not galeria:
        raise HTTPException(status_code=404, detail="Galería no encontrada")
    return galeria

def _obras_publicas_del_artista(session: Session, artista_id: int) -> List[ObraPublicRead]:
    """
    Obras veladas del artista: SIN precio, SIN notas internas.
    Es la misma filosofía de Interface Segregation que PublicObra (Fase 2).
    """
    obras = session.exec(
        select(Obra).where(
            Obra.artista_id == artista_id,
            Obra.activo == True,
        ).order_by(Obra.anio.desc())  # type: ignore[attr-defined]
    ).all()

    resultado = []
    for obra in obras:
        tecnica_nombre = None
        if obra.tecnica_id:
            tecnica = session.get(Tecnica, obra.tecnica_id)
            tecnica_nombre = tecnica.nombre if tecnica else None

        resultado.append(
            ObraPublicRead(
                id=obra.id,
                titulo=obra.titulo,
                anio=obra.anio,
                estado=obra.estado.value if hasattr(obra.estado, "value") else str(obra.estado),
                imagen_url=obra.imagen_url,
                tecnica_nombre=tecnica_nombre,
                statement=obra.statement,
            )
        )
    return resultado

# ==========================================
# REGISTRO SELF-SERVICE (PÚBLICO)
# IMPORTANTE: este endpoint debe ir ANTES de /{slug}
# para que FastAPI no confunda "register" con un slug
# ==========================================
@router.post("/register", response_model=GaleriaRegisterResponse, status_code=201)
def registrar_galeria(
    data: GaleriaRegisterRequest,
    session: Session = Depends(get_session),
):
    """
    Registro público: crea una galería + su dueño (ADMIN) en una sola operación.
    
    Devuelve tokens de acceso para autologin inmediato.
    No requiere autenticación (es el punto de entrada de nuevas galerías).
    
    Flujo:
    1. Valida email único + slug único
    2. Crea UserAccount (sin rol global)
    3. Crea Galeria con slug derivado del nombre
    4. Asigna UserGalleryRole.ADMIN al dueño en la nueva galería
    5. Setea galeria_id_activa
    6. Genera tokens JWT
    """
    service = GaleriaService(session)
    return service.registrar_galeria(
        nombre_galeria=data.nombre_galeria,
        email_dueno=data.email_dueno,
        nombre_dueno=data.nombre_dueno,
        password_dueno=data.password_dueno,
        bio_galeria=data.bio_galeria,
        ubicacion_galeria=data.ubicacion_galeria,
        sitio_web_galeria=data.sitio_web_galeria,
    )

# ==========================================
# PERFIL PÚBLICO DE GALERÍA
# ==========================================
@router.get("/{slug}", response_model=GaleriaPublicRead)
def obtener_galeria_publica(slug: str, session: Session = Depends(get_session)):
    """Perfil público de la galería: bio, ubicación y contadores."""
    galeria = _obtener_galeria_activa_o_404(session, slug)

    total_artistas = session.exec(
        select(func.count(Artista.id)).where(
            Artista.galeria_id == galeria.id,
            Artista.activo == True,
        )
    ).one()

    total_obras = session.exec(
        select(func.count(Obra.id)).where(
            Obra.galeria_id == galeria.id,
            Obra.activo == True,
        )
    ).one()

    return GaleriaPublicRead(
        id=galeria.id,
        nombre=galeria.nombre,
        slug=galeria.slug,
        bio=galeria.bio,
        ubicacion=galeria.ubicacion,
        sitio_web=galeria.sitio_web,
        logo_url=galeria.logo_url,
        total_artistas=total_artistas,
        total_obras=total_obras,
    )

# ==========================================
# LISTADO PÚBLICO DE ARTISTAS
# ==========================================
@router.get("/{slug}/artistas", response_model=List[ArtistaPublicRead])
def listar_artistas_publicos(slug: str, session: Session = Depends(get_session)):
    """Artistas activos de la galería, ordenados por nombre."""
    galeria = _obtener_galeria_activa_o_404(session, slug)

    artistas = session.exec(
        select(Artista).where(
            Artista.galeria_id == galeria.id,
            Artista.activo == True,
        ).order_by(Artista.nombre)  # type: ignore[attr-defined]
    ).all()
    return artistas

# ==========================================
# PERFIL PÚBLICO DE ARTISTA + OBRAS VELADAS
# ==========================================
@router.get("/{slug}/artistas/{artista_slug}", response_model=ArtistaDetallePublicRead)
def obtener_artista_publico(
    slug: str,
    artista_slug: str,
    session: Session = Depends(get_session),
):
    """
    Perfil del artista con sus obras veladas.
    Aislamiento: el artista debe pertenecer a ESTA galería (404 si no).
    """
    galeria = _obtener_galeria_activa_o_404(session, slug)

    artista = session.exec(
        select(Artista).where(
            Artista.galeria_id == galeria.id,
            Artista.slug == artista_slug,
            Artista.activo == True,
        )
    ).first()
    if not artista:
        raise HTTPException(status_code=404, detail="Artista no encontrado en esta galería")

    obras = _obras_publicas_del_artista(session, artista.id)

    return ArtistaDetallePublicRead(
        id=artista.id,
        nombre=artista.nombre,
        slug=artista.slug,
        bio=artista.bio,
        nacionalidad=artista.nacionalidad,
        anio_nacimiento=artista.anio_nacimiento,
        foto_perfil=artista.foto_perfil,
        sitio_web=artista.sitio_web,
        obras=obras,
    )