"""Tests del modelo Artista (Fase 3, Tarea 2)."""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models.galeria import Galeria
from app.models.artista import Artista


def _crear_galeria(session: Session, nombre: str, slug: str) -> Galeria:
    """Helper: crea una galería y la devuelve con id cargado."""
    galeria = Galeria(nombre=nombre, slug=slug)
    session.add(galeria)
    session.commit()
    session.refresh(galeria)
    return galeria


def test_crear_artista_vinculado_a_galeria(session: Session):
    """Un artista se crea correctamente vinculado a su galería."""
    galeria = _crear_galeria(session, "Galería Sur", "galeria-sur")

    artista = Artista(
        galeria_id=galeria.id,
        nombre="Julio Le Parc",
        slug="julio-le-parc",
        bio="Artista cinético argentino",
        nacionalidad="Argentina",
        anio_nacimiento=1928,
    )
    session.add(artista)
    session.commit()
    session.refresh(artista)

    assert artista.id is not None
    assert artista.galeria_id == galeria.id
    assert artista.activo is True
    assert artista.fecha_creacion is not None


def test_slug_unico_por_galeria_pero_repetible_entre_galerias(session: Session):
    """
    Regla de negocio del multi-tenancy:
    - Dos galerías PUEDEN tener un artista con el mismo slug.
    - Una galería NO puede tener dos artistas con el mismo slug.
    """
    g1 = _crear_galeria(session, "Galería Uno", "galeria-uno")
    g2 = _crear_galeria(session, "Galería Dos", "galeria-dos")

    # Mismo slug en galerías DISTINTAS: permitido
    a1 = Artista(galeria_id=g1.id, nombre="María López", slug="maria-lopez")
    a2 = Artista(galeria_id=g2.id, nombre="María López de Norte", slug="maria-lopez")
    session.add(a1)
    session.add(a2)
    session.commit()  # No debe fallar

    # Mismo slug en la MISMA galería: debe fallar
    a3 = Artista(galeria_id=g1.id, nombre="María López duplicada", slug="maria-lopez")
    session.add(a3)
    with pytest.raises(IntegrityError):
        session.commit()


def test_artista_soft_delete(session: Session):
    """Desactivar un artista no lo borra de la BD."""
    galeria = _crear_galeria(session, "Galería Temp", "galeria-temp")
    artista = Artista(galeria_id=galeria.id, nombre="Artista X", slug="artista-x")
    session.add(artista)
    session.commit()
    session.refresh(artista)

    artista.activo = False
    session.add(artista)
    session.commit()
    session.refresh(artista)

    assert artista.activo is False
    assert session.get(Artista, artista.id) is not None


def test_relacion_galeria_artistas(session: Session):
    """Se puede navegar de la galería a sus artistas (galeria.artistas)."""
    galeria = _crear_galeria(session, "Galería Rel", "galeria-rel")
    session.add(Artista(galeria_id=galeria.id, nombre="Artista 1", slug="a1"))
    session.add(Artista(galeria_id=galeria.id, nombre="Artista 2", slug="a2"))
    session.commit()

    # Re-leemos la galería desde cero para validar la relación
    galeria_fresca = session.get(Galeria, galeria.id)
    assert len(galeria_fresca.artistas) == 2
    nombres = {a.nombre for a in galeria_fresca.artistas}
    assert nombres == {"Artista 1", "Artista 2"}