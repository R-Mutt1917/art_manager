"""
Tests de aislamiento multi-tenant para Préstamos.
"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.usuario import Usuario, RolUsuario
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.tecnica import Tecnica
from app.models.obra import Obra
from app.core.security import hash_password


def _crear_usuario_en_galeria(session: Session, email: str, slug: str):
    galeria = Galeria(nombre=f"G {slug}", slug=slug)
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    artista = Artista(galeria_id=galeria.id, nombre=f"Art {slug}", slug=f"art-{slug}")
    session.add(artista)
    session.commit()

    usuario = Usuario(
        email=email,
        nombre=f"User {slug}",
        password_hash=hash_password("password123"),
        rol=RolUsuario.ADMIN,
        galeria_id=galeria.id,
    )
    session.add(usuario)
    session.commit()
    return usuario, galeria, artista


def _crear_obra_en_galeria(session: Session, galeria: Galeria, artista: Artista, titulo: str) -> Obra:
    tecnica = Tecnica(nombre=f"Téc {titulo}")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    obra = Obra(
        titulo=titulo,
        anio=2026,
        dimensiones="50x50",
        galeria_id=galeria.id,
        artista_id=artista.id,
        tecnica_id=tecnica.id,
    )
    session.add(obra)
    session.commit()
    session.refresh(obra)
    return obra


def _login(client: TestClient, email: str) -> dict:
    r = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.json()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_usuario_no_ve_prestamos_activos_de_otra_galeria(client: TestClient, session: Session):
    """Usuario B no ve préstamos activos creados por usuario A."""
    _crear_usuario_en_galeria(session, "prest_a@test.com", "g-prest-a")
    _crear_usuario_en_galeria(session, "prest_b@test.com", "g-prest-b")

    _, galeria_a, artista_a = (
        session.get(Usuario, session.exec(
            __import__("sqlmodel").select(Usuario).where(Usuario.email == "prest_a@test.com")
        ).first().id).galeria, None, None
    )
    # Re-obtener con más cuidado
    user_a = session.exec(
        __import__("sqlmodel").select(Usuario).where(Usuario.email == "prest_a@test.com")
    ).first()
    galeria_a = session.get(Galeria, user_a.galeria_id)
    artista_a = session.exec(
        __import__("sqlmodel").select(Artista).where(Artista.galeria_id == galeria_a.id)
    ).first()

    obra_a = _crear_obra_en_galeria(session, galeria_a, artista_a, "Obra para A")

    headers_a = _login(client, "prest_a@test.com")
    headers_b = _login(client, "prest_b@test.com")

    # A presta su obra
    r = client.post(
        "/prestamos/",
        json={
            "obra_id": obra_a.id,
            "prestatario_nombre": "Museo X",
            "fecha_prestamo": "2026-01-01",
            "fecha_devolucion_esperada": "2026-06-01",
        },
        headers=headers_a,
    )
    assert r.status_code == 201, r.json()

    # A lo ve en sus activos
    r = client.get("/prestamos/activos", headers=headers_a)
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # B NO lo ve
    r = client.get("/prestamos/activos", headers=headers_b)
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_usuario_no_puede_registrar_devolucion_de_prestamo_ajeno(client: TestClient, session: Session):
    """Usuario B no puede devolver un préstamo que creó usuario A."""
    _crear_usuario_en_galeria(session, "dev_a@test.com", "g-dev-a")
    _crear_usuario_en_galeria(session, "dev_b@test.com", "g-dev-b")

    user_a = session.exec(
        __import__("sqlmodel").select(Usuario).where(Usuario.email == "dev_a@test.com")
    ).first()
    galeria_a = session.get(Galeria, user_a.galeria_id)
    artista_a = session.exec(
        __import__("sqlmodel").select(Artista).where(Artista.galeria_id == galeria_a.id)
    ).first()

    obra_a = _crear_obra_en_galeria(session, galeria_a, artista_a, "Obra dev A")

    headers_a = _login(client, "dev_a@test.com")
    headers_b = _login(client, "dev_b@test.com")

    # A crea préstamo
    r = client.post(
        "/prestamos/",
        json={
            "obra_id": obra_a.id,
            "prestatario_nombre": "Museo Y",
            "fecha_prestamo": "2026-01-01",
            "fecha_devolucion_esperada": "2026-06-01",
        },
        headers=headers_a,
    )
    prestamo_id = r.json()["id"]

    # B intenta devolverlo → 404 (no filtra existencia)
    r = client.post(
        f"/prestamos/{prestamo_id}/devolucion",
        json={
            "fecha_devolucion_real": "2026-05-30",
            "condicion_retorno": "Buena",
            "estado_obra_tras_devolucion": "disponible",
        },
        headers=headers_b,
    )
    assert r.status_code == 404, "B no debe poder devolver préstamo de A"