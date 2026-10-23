"""
Tests críticos de aislamiento multi-tenant.
Garantizan que un usuario de la Galería A NO PUEDE acceder
a datos de la Galería B bajo ninguna circunstancia.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.usuario import Usuario, RolUsuario
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.tecnica import Tecnica
from app.core.security import hash_password

def _crear_usuario_en_galeria(
    session: Session,
    email: str,
    galeria_slug: str,
    rol=RolUsuario.ADMIN,
) -> tuple[Usuario, Galeria]:
    """Helper: crea una galería + usuario asociado."""
    galeria = Galeria(
        nombre=f"Galería {galeria_slug}",
        slug=galeria_slug,
    )
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    usuario = Usuario(
        email=email,
        nombre=f"User {galeria_slug}",
        password_hash=hash_password("password123"),
        rol=rol,
        galeria_id=galeria.id,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return usuario, galeria

def _login(client: TestClient, email: str) -> dict:
    """Helper: devuelve headers de auth para un usuario."""
    r = client.post("/auth/login", json={
        "email": email,
        "password": "password123",
    })
    assert r.status_code == 200, f"Login falló para {email}: {r.json()}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_usuario_no_puede_ver_obras_de_otra_galeria(client: TestClient, session: Session):
    """
    TEST ESTRELLA del multi-tenancy:
    Usuario de Galería A crea una obra.
    Usuario de Galería B NO puede verla, aunque intente GET /obras/{id} directo.
    """
    # Setup: 2 galerías, 2 usuarios, 1 técnica compartida
    user_a, galeria_a = _crear_usuario_en_galeria(session, "user_a@test.com", "galeria-a")
    user_b, galeria_b = _crear_usuario_en_galeria(session, "user_b@test.com", "galeria-b")

    tecnica = Tecnica(nombre="Óleo aislamiento")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    # Artista de Galería A
    artista_a = Artista(galeria_id=galeria_a.id, nombre="Artista A", slug="artista-a")
    session.add(artista_a)
    session.commit()
    session.refresh(artista_a)

    headers_a = _login(client, "user_a@test.com")
    headers_b = _login(client, "user_b@test.com")

    # Usuario A crea una obra en su galería
    r = client.post(
        "/obras/",
        data={
            "titulo": "Obra secreta de A",
            "anio": "2026",
            "dimensiones": "100x100",
            "tecnica": "Óleo aislamiento",
        },
        headers=headers_a,
    )
    assert r.status_code == 201
    obra_id = r.json()["id"]
    assert r.json()["galeria_id"] == galeria_a.id

    # Usuario A PUEDE verla
    r = client.get(f"/obras/{obra_id}", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["titulo"] == "Obra secreta de A"

    # Usuario B NO puede verla (debe dar 404, no 403, para no filtrar existencia)
    r = client.get(f"/obras/{obra_id}", headers=headers_b)
    assert r.status_code == 404, "Usuario B NO debe poder ver obra de Galería A"

    # Listado: Usuario B NO ve la obra de A
    r = client.get("/obras/", headers=headers_b)
    assert r.status_code == 200
    ids_b = [o["id"] for o in r.json()]
    assert obra_id not in ids_b, "Listado de B no debe incluir obras de A"

def test_usuario_no_puede_editar_obras_de_otra_galeria(client: TestClient, session: Session):
    """Usuario de Galería B no puede PUT sobre obra de Galería A."""
    user_a, galeria_a = _crear_usuario_en_galeria(session, "user_edit_a@test.com", "galeria-edit-a")
    _crear_usuario_en_galeria(session, "user_edit_b@test.com", "galeria-edit-b")

    tecnica = Tecnica(nombre="Acrílico edit")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    artista_a = Artista(galeria_id=galeria_a.id, nombre="Artista Edit A", slug="artista-edit-a")
    session.add(artista_a)
    session.commit()
    session.refresh(artista_a)

    headers_a = _login(client, "user_edit_a@test.com")
    headers_b = _login(client, "user_edit_b@test.com")

    # A crea obra
    r = client.post(
        "/obras/",
        data={
            "titulo": "Obra protegida",
            "anio": "2026",
            "dimensiones": "50x50",
            "tecnica": "Acrílico edit",
        },
        headers=headers_a,
    )
    obra_id = r.json()["id"]

    # B intenta editarla → debe fallar (404 para no filtrar existencia)
    r = client.put(
        f"/obras/{obra_id}",
        data={
            "titulo": "HACKED POR B",
            "anio": "2026",
            "dimensiones": "50x50",
            "tecnica": "Acrílico edit",
        },
        headers=headers_b,
    )
    assert r.status_code == 404

    # Verificar que la obra NO fue modificada
    r = client.get(f"/obras/{obra_id}", headers=headers_a)
    assert r.json()["titulo"] == "Obra protegida"

def test_usuario_no_puede_eliminar_obras_de_otra_galeria(client: TestClient, session: Session):
    """Usuario de Galería B no puede DELETE sobre obra de Galería A."""
    user_a, galeria_a = _crear_usuario_en_galeria(session, "user_del_a@test.com", "galeria-del-a")
    _crear_usuario_en_galeria(session, "user_del_b@test.com", "galeria-del-b")

    tecnica = Tecnica(nombre="Mixta delete")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    artista_a = Artista(galeria_id=galeria_a.id, nombre="Artista Del A", slug="artista-del-a")
    session.add(artista_a)
    session.commit()
    session.refresh(artista_a)

    headers_a = _login(client, "user_del_a@test.com")
    headers_b = _login(client, "user_del_b@test.com")

    r = client.post(
        "/obras/",
        data={
            "titulo": "Obra a proteger",
            "anio": "2026",
            "dimensiones": "30x30",
            "tecnica": "Mixta delete",
        },
        headers=headers_a,
    )
    obra_id = r.json()["id"]

    # B intenta eliminarla
    r = client.delete(f"/obras/{obra_id}", headers=headers_b)
    assert r.status_code == 404

    # La obra sigue activa para A
    r = client.get(f"/obras/{obra_id}", headers=headers_a)
    assert r.status_code == 200

def test_usuario_sin_galeria_recibe_403(client: TestClient, session: Session):
    """Un usuario sin galeria_id asignada recibe 403, no 500."""
    usuario = Usuario(
        email="user_sin_galeria@test.com",
        nombre="Sin Galería",
        password_hash=hash_password("password123"),
        rol=RolUsuario.ADMIN,
        galeria_id=None,  # Sin galería
    )
    session.add(usuario)
    session.commit()

    headers = _login(client, "user_sin_galeria@test.com")
    r = client.get("/obras/", headers=headers)
    assert r.status_code == 403, "Usuario sin galería debe recibir 403"