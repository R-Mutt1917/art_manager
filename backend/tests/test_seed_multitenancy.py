"""
Tests del seed de Galería Demo y migración de obras (Fase 3, Tarea 4).
"""
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.obra import Obra
from app.models.tecnica import Tecnica


def test_seed_crea_galeria_demo(client: TestClient, session: Session):
    """Al arrancar la app, se crea la Galería Demo automáticamente."""
    galeria = session.exec(
        select(Galeria).where(Galeria.slug == "galeria-demo")
    ).first()
    
    assert galeria is not None
    assert galeria.nombre == "Galería Demo"
    assert galeria.activo is True


def test_seed_crea_artista_demo(client: TestClient, session: Session):
    """Al arrancar la app, se crea el Artista Demo en la Galería Demo."""
    galeria = session.exec(
        select(Galeria).where(Galeria.slug == "galeria-demo")
    ).first()
    
    artista = session.exec(
        select(Artista).where(Artista.slug == "artista-demo")
    ).first()
    
    assert artista is not None
    assert artista.nombre == "Artista Demo"
    assert artista.galeria_id == galeria.id


def test_obras_existentes_se_migran_a_galeria_demo(client: TestClient, session: Session):
    """
    Si creamos una obra SIN galeria_id (como las viejas),
    el seed la migra automáticamente a la Galería Demo.
    """
    # Crear una técnica
    tecnica = Tecnica(nombre="Óleo migración")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)
    
    # Crear obra sin galería (simulando dato legacy)
    obra = Obra(
        titulo="Obra legacy",
        anio=2025,
        dimensiones="50x50 cm",
        tecnica_id=tecnica.id,
        galeria_id=None,  # Sin galería
        artista_id=None,  # Sin artista
    )
    session.add(obra)
    session.commit()
    session.refresh(obra)
    
    # Llamar manualmente a la migración (en producción corre en lifespan)
    from app.seed import seed_galeria_demo, seed_artista_demo, migrar_obras_a_galeria_demo
    galeria = seed_galeria_demo(session)
    artista = seed_artista_demo(session, galeria)
    migrar_obras_a_galeria_demo(session, galeria, artista)
    
    # Verificar que la obra ahora tiene galería y artista
    session.refresh(obra)
    assert obra.galeria_id == galeria.id
    assert obra.artista_id == artista.id


def test_post_obras_asigna_galeria_demo_por_defecto(client: TestClient, auth_headers: dict):
    """
    POST /obras/ sin especificar galeria_id asigna la Galería Demo automáticamente.
    """
    # Crear obra sin especificar galería
    r = client.post(
        "/obras/",
        data={
            "titulo": "Obra automática",
            "anio": "2026",
            "dimensiones": "100x100 cm",
            "tecnica": "Acrílico",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()
    
    obra_data = r.json()
    assert obra_data["galeria_id"] is not None
    assert obra_data["artista_id"] is not None