"""
Tests del multi-tenancy en el modelo Obra (Fase 3, Tarea 3).
Valida que las FKs a Galeria y Artista funcionan sin romper
los tests existentes (que crean obras sin galería/artista).
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.obra import Obra
from app.models.tecnica import Tecnica


def _seed_base(session: Session):
    """Crea galería + artista + técnica base para los tests."""
    galeria = Galeria(nombre="Galería Test", slug="galeria-test")
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    artista = Artista(
        galeria_id=galeria.id,
        nombre="Artista Test",
        slug="artista-test",
    )
    session.add(artista)
    session.commit()
    session.refresh(artista)

    tecnica = Tecnica(nombre="Óleo sobre lienzo")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    return galeria, artista, tecnica


def test_obra_con_galeria_y_artista(session: Session):
    """Se puede crear una obra vinculada a galería y artista."""
    galeria, artista, tecnica = _seed_base(session)

    obra = Obra(
        titulo="Obra con tenant",
        anio=2026,
        dimensiones="100x100 cm",
        galeria_id=galeria.id,
        artista_id=artista.id,
        tecnica_id=tecnica.id,
    )
    session.add(obra)
    session.commit()
    session.refresh(obra)

    assert obra.id is not None
    assert obra.galeria_id == galeria.id
    assert obra.artista_id == artista.id


def test_obra_sin_galeria_ni_artista_sigue_funcionando(session: Session):
    """
    COMPATIBILIDAD: una obra puede crearse sin galería ni artista.
    Esto es clave para no romper los 40 tests existentes.
    En la Fase B (T4) vamos a migrar estos datos a la Galería Demo.
    """
    tecnica = Tecnica(nombre="Acuarela")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    obra = Obra(
        titulo="Obra legacy",
        anio=2025,
        dimensiones="50x50 cm",
        tecnica_id=tecnica.id,
    )
    session.add(obra)
    session.commit()
    session.refresh(obra)

    assert obra.id is not None
    assert obra.galeria_id is None
    assert obra.artista_id is None


def test_consulta_por_galeria(session: Session):
    """Se pueden filtrar obras por galería (query base del multi-tenancy)."""
    g1 = Galeria(nombre="Galería A", slug="galeria-a")
    g2 = Galeria(nombre="Galería B", slug="galeria-b")
    session.add(g1)
    session.add(g2)
    session.commit()
    session.refresh(g1)
    session.refresh(g2)

    tecnica = Tecnica(nombre="Acrílico")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    # 3 obras en Galería A, 2 obras en Galería B
    for i in range(3):
        session.add(Obra(
            titulo=f"Obra A-{i}", anio=2026,
            dimensiones="100x100 cm", galeria_id=g1.id, tecnica_id=tecnica.id,
        ))
    for i in range(2):
        session.add(Obra(
            titulo=f"Obra B-{i}", anio=2026,
            dimensiones="100x100 cm", galeria_id=g2.id, tecnica_id=tecnica.id,
        ))
    session.commit()

    # Filtrar solo Galería A: debe devolver exactamente 3
    obras_g1 = session.exec(
        select(Obra).where(Obra.galeria_id == g1.id)
    ).all()
    assert len(obras_g1) == 3

    obras_g2 = session.exec(
        select(Obra).where(Obra.galeria_id == g2.id)
    ).all()
    assert len(obras_g2) == 2


def test_navegacion_galeria_obras(session: Session):
    """Se puede navegar galeria -> obras via la relación."""
    galeria = Galeria(nombre="Galería Nav", slug="galeria-nav")
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    tecnica = Tecnica(nombre="Mixta")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    session.add(Obra(
        titulo="Obra 1", anio=2026, dimensiones="1x1",
        galeria_id=galeria.id, tecnica_id=tecnica.id,
    ))
    session.add(Obra(
        titulo="Obra 2", anio=2026, dimensiones="2x2",
        galeria_id=galeria.id, tecnica_id=tecnica.id,
    ))
    session.commit()

    galeria_fresca = session.get(Galeria, galeria.id)
    assert len(galeria_fresca.obras) == 2
    titulos = {o.titulo for o in galeria_fresca.obras}
    assert titulos == {"Obra 1", "Obra 2"}


def test_fk_invalida_rechaza_guardado(session: Session):
    """No se puede crear obra con galeria_id inexistente (integridad de FK)."""
    tecnica = Tecnica(nombre="Técnica X")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    obra = Obra(
        titulo="Obra huérfana",
        anio=2026,
        dimensiones="1x1",
        galeria_id=99999,  # No existe
        tecnica_id=tecnica.id,
    )
    session.add(obra)
    with pytest.raises(IntegrityError):
        session.commit()