"""
Tests de aislamiento multi-tenant para Compradores.
Garantizan que un usuario de Galería A no ve compradores de Galería B.
"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.usuario import Usuario, RolUsuario
from app.models.galeria import Galeria
from app.models.comprador import Comprador
from app.core.security import hash_password


def _crear_usuario_en_galeria(session: Session, email: str, slug: str):
    galeria = Galeria(nombre=f"G {slug}", slug=slug)
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    usuario = Usuario(
        email=email,
        nombre=f"User {slug}",
        password_hash=hash_password("password123"),
        rol=RolUsuario.ADMIN,
        galeria_id=galeria.id,
    )
    session.add(usuario)
    session.commit()
    return usuario, galeria


def _login(client: TestClient, email: str) -> dict:
    r = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.json()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_usuario_no_ve_compradores_de_otra_galeria(client: TestClient, session: Session):
    """Usuario de Galería B NO ve al comprador creado por Usuario de Galería A."""
    _crear_usuario_en_galeria(session, "user_comp_a@test.com", "g-comp-a")
    _crear_usuario_en_galeria(session, "user_comp_b@test.com", "g-comp-b")

    headers_a = _login(client, "user_comp_a@test.com")
    headers_b = _login(client, "user_comp_b@test.com")

    # A crea un comprador
    r = client.post(
        "/compradores/",
        json={
            "nombre": "Cliente Secreto de A",
            "email": "cliente_secreto@a.com",
            "telefono": "1111",
        },
        headers=headers_a,
    )
    assert r.status_code == 201
    comprador_id = r.json()["id"]

    # A lo ve
    r = client.get(f"/compradores/{comprador_id}", headers=headers_a)
    assert r.status_code == 200

    # B NO lo ve (404, no 403, para no filtrar existencia)
    r = client.get(f"/compradores/{comprador_id}", headers=headers_b)
    assert r.status_code == 404

    # B no lo ve en el listado tampoco
    r = client.get("/compradores/", headers=headers_b)
    assert r.status_code == 200
    ids_b = [c["id"] for c in r.json()]
    assert comprador_id not in ids_b