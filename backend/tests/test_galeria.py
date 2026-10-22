"""Tests del modelo Galeria (Fase 3, Tarea 1)."""
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.galeria import Galeria


def test_crear_galeria_basica(session: Session):
    """Se puede crear una galería con los campos mínimos."""
    galeria = Galeria(
        nombre="Galería Sur",
        slug="galeria-sur",
        bio="Galería de arte contemporáneo en Buenos Aires",
        ubicacion="Buenos Aires, Argentina",
    )
    session.add(galeria)
    session.commit()
    session.refresh(galeria)
    
    assert galeria.id is not None
    assert galeria.nombre == "Galería Sur"
    assert galeria.slug == "galeria-sur"
    assert galeria.activo is True
    assert galeria.fecha_creacion is not None


def test_galeria_slug_unico(session: Session):
    """El slug debe ser único (dos galerías no pueden tener el mismo slug)."""
    galeria1 = Galeria(nombre="Galería Uno", slug="slug-test")
    session.add(galeria1)
    session.commit()
    
    galeria2 = Galeria(nombre="Galería Dos", slug="slug-test")  # Mismo slug
    session.add(galeria2)
    
    # Debería fallar al commitear por constraint unique
    from sqlalchemy.exc import IntegrityError
    import pytest
    with pytest.raises(IntegrityError):
        session.commit()


def test_galeria_se_puede_desactivar(session: Session):
    """Se puede desactivar una galería sin borrarla (soft delete)."""
    galeria = Galeria(nombre="Galería Temporal", slug="galeria-temporal")
    session.add(galeria)
    session.commit()
    session.refresh(galeria)
    
    # Desactivar
    galeria.activo = False
    session.add(galeria)
    session.commit()
    session.refresh(galeria)
    
    assert galeria.activo is False
    
    # Pero sigue en la BD
    encontrada = session.get(Galeria, galeria.id)
    assert encontrada is not None
    assert encontrada.nombre == "Galería Temporal"