"""
Tests de endpoints públicos de galerías (URLs semánticas, Fase 3 T6-1).
Validan que lo público es público y lo privado sigue velado.
"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.tecnica import Tecnica
from app.models.obra import Obra

def _seed_galerias_con_artistas_y_obras(session: Session):
    """Galería Sur (activa, 1 artista activo + 1 inactivo + 1 obra) y Galería Norte."""
    galeria = Galeria(
        nombre="Galería Sur",
        slug="galeria-sur",
        bio="Arte contemporáneo",
        ubicacion="Buenos Aires",
    )
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    artista = Artista(
        galeria_id=galeria.id,
        nombre="Julio Le Parc",
        slug="julio-le-parc",
        bio="Artista cinético",
        nacionalidad="Argentina",
    )
    session.add(artista)

    artista_inactivo = Artista(
        galeria_id=galeria.id,
        nombre="Artista Retirado",
        slug="artista-retirado",
        activo=False,
    )
    session.add(artista_inactivo)

    tecnica = Tecnica(nombre="Técnica mixta")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)
    session.refresh(artista)

    obra = Obra(
        titulo="Continuelumière",
        anio=1966,
        dimensiones="100x100",
        precio=50000.0,
        notas="NOTA INTERNA CONFIDENCIAL",
        galeria_id=galeria.id,
        artista_id=artista.id,
        tecnica_id=tecnica.id,
    )
    session.add(obra)
    session.commit()

    g2 = Galeria(nombre="Galería Norte", slug="galeria-norte")
    session.add(g2)
    session.commit()
    session.refresh(g2)

    a2 = Artista(galeria_id=g2.id, nombre="Otra Artista", slug="otra-artista")
    session.add(a2)
    session.commit()

def test_galeria_publica_devuelve_perfil_con_contadores(client: TestClient, session: Session):
    """El perfil público incluye contadores y excluye artistas inactivos."""
    _seed_galerias_con_artistas_y_obras(session)

    r = client.get("/galerias/galeria-sur")
    assert r.status_code == 200
    data = r.json()
    assert data["nombre"] == "Galería Sur"
    assert data["slug"] == "galeria-sur"
    assert data["total_artistas"] == 1  # el inactivo no cuenta
    assert data["total_obras"] == 1

def test_galeria_inexistente_devuelve_404(client: TestClient, session: Session):
    r = client.get("/galerias/no-existe")
    assert r.status_code == 404

def test_listado_artistas_publicos_excluye_inactivos(client: TestClient, session: Session):
    _seed_galerias_con_artistas_y_obras(session)

    r = client.get("/galerias/galeria-sur/artistas")
    assert r.status_code == 200
    slugs = [a["slug"] for a in r.json()]
    assert slugs == ["julio-le-parc"]

def test_detalle_artista_vela_precio_y_notas_internas(client: TestClient, session: Session):
    """
    TEST CLAVE de velado: el perfil público del artista muestra obras
    SIN precio y SIN notas internas del curador.
    """
    _seed_galerias_con_artistas_y_obras(session)

    r = client.get("/galerias/galeria-sur/artistas/julio-le-parc")
    assert r.status_code == 200
    data = r.json()
    assert data["nombre"] == "Julio Le Parc"
    assert len(data["obras"]) == 1

    obra = data["obras"][0]
    assert obra["titulo"] == "Continuelumière"
    assert obra["tecnica_nombre"] == "Técnica mixta"

    # Velado: ni precio ni notas internas en el payload
    assert "precio" not in obra
    assert "notas" not in obra
    assert "CONFIDENCIAL" not in str(data)

def test_artista_de_otra_galeria_no_responde_bajo_slug_ajeno(client: TestClient, session: Session):
    """Aislamiento en lo público: /galeria-sur/artistas/otra-artista → 404."""
    _seed_galerias_con_artistas_y_obras(session)

    r = client.get("/galerias/galeria-sur/artistas/otra-artista")
    assert r.status_code == 404