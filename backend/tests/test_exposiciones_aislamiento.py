"""
Tests de aislamiento multi-tenant para Exposiciones.
"""
from fastapi.testclient import TestClient
from sqlmodel import Session, select

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
    tecnica = Tecnica(nombre=f"Téc expo {titulo}")
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


def test_usuario_no_puede_asignar_obras_a_exposicion_de_otra_galeria(client: TestClient, session: Session):
    """Usuario B no puede asignar su obra a una exposición creada por A."""
    _crear_usuario_en_galeria(session, "expo_a@test.com", "g-expo-a")
    _crear_usuario_en_galeria(session, "expo_b@test.com", "g-expo-b")

    user_a = session.exec(select(Usuario).where(Usuario.email == "expo_a@test.com")).first()
    galeria_a = session.get(Galeria, user_a.galeria_id)
    artista_a = session.exec(select(Artista).where(Artista.galeria_id == galeria_a.id)).first()

    user_b = session.exec(select(Usuario).where(Usuario.email == "expo_b@test.com")).first()
    galeria_b = session.get(Galeria, user_b.galeria_id)
    artista_b = session.exec(select(Artista).where(Artista.galeria_id == galeria_b.id)).first()

    # A crea una exposición
    headers_a = _login(client, "expo_a@test.com")
    r = client.post(
        "/exposiciones/",
        json={
            "nombre": "Expo de A",
            "lugar": "Sala A",
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-03-31",
        },
        headers=headers_a,
    )
    assert r.status_code == 201, r.json()
    expo_a_id = r.json()["id"]

    # B crea una obra en SU galería
    obra_b = _crear_obra_en_galeria(session, galeria_b, artista_b, "Obra de B")
    headers_b = _login(client, "expo_b@test.com")

    # B intenta asignar SU obra a la exposición de A → debe fallar
    r = client.post(
        f"/exposiciones/{expo_a_id}/obras/{obra_b.id}",
        json={"fecha_ingreso": "2026-03-05", "fecha_retiro_esperada": "2026-03-25"},
        headers=headers_b,
    )
    # 404 porque la exposición no pertenece a la galería de B
    assert r.status_code == 404, "B no debe ver la exposición de A"


def test_usuario_no_puede_ver_checklist_de_exposicion_ajena(client: TestClient, session: Session):
    """Usuario B no puede ver el checklist de una exposición de A."""
    _crear_usuario_en_galeria(session, "check_a@test.com", "g-check-a")
    _crear_usuario_en_galeria(session, "check_b@test.com", "g-check-b")

    user_a = session.exec(select(Usuario).where(Usuario.email == "check_a@test.com")).first()
    galeria_a = session.get(Galeria, user_a.galeria_id)
    artista_a = session.exec(select(Artista).where(Artista.galeria_id == galeria_a.id)).first()

    headers_a = _login(client, "check_a@test.com")
    headers_b = _login(client, "check_b@test.com")

    # A crea exposición
    r = client.post(
        "/exposiciones/",
        json={
            "nombre": "Expo Secreta A",
            "lugar": "Sala Privada",
            "fecha_inicio": "2026-04-01",
            "fecha_fin": "2026-04-30",
        },
        headers=headers_a,
    )
    expo_a_id = r.json()["id"]

    # A ve su checklist
    r = client.get(f"/exposiciones/{expo_a_id}/checklist", headers=headers_a)
    assert r.status_code == 200

    # B NO puede ver el checklist
    r = client.get(f"/exposiciones/{expo_a_id}/checklist", headers=headers_b)
    assert r.status_code == 404, "B no debe acceder al checklist de A"