"""
Tests de aislamiento multi-tenant para el Dashboard.
Las métricas agregadas (COUNT/SUM/GROUP BY) deben respetar el tenant.
"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.usuario import Usuario, RolUsuario
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.tecnica import Tecnica
from app.models.obra import Obra
from app.core.security import hash_password

def _setup_galeria_con_obras(
    session: Session,
    email: str,
    slug: str,
    n_obras: int,
    precio: float,
) -> Galeria:
    """Crea galería + artista + técnica + N obras con precio + usuario admin."""
    galeria = Galeria(nombre=f"G {slug}", slug=slug)
    session.add(galeria)
    session.commit()
    session.refresh(galeria)

    artista = Artista(galeria_id=galeria.id, nombre=f"Art {slug}", slug=f"art-{slug}")
    session.add(artista)
    session.commit()
    session.refresh(artista)

    tecnica = Tecnica(nombre=f"Téc {slug}")
    session.add(tecnica)
    session.commit()
    session.refresh(tecnica)

    for i in range(n_obras):
        session.add(Obra(
            titulo=f"Obra {slug} {i}",
            anio=2026,
            dimensiones="50x50",
            precio=precio,
            galeria_id=galeria.id,
            artista_id=artista.id,
            tecnica_id=tecnica.id,
        ))
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
    return galeria

def _login(client: TestClient, email: str) -> dict:
    r = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.json()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_dashboard_muestra_solo_metricas_de_la_galeria_propia(client: TestClient, session: Session):
    """
    TEST CLAVE de métricas aisladas:
    Galería A tiene 3 obras de $1000, Galería B tiene 1 obra de $500.
    Cada dashboard debe reflejar SOLO sus propios números.
    """
    _setup_galeria_con_obras(session, "dash_a@test.com", "g-dash-a", n_obras=3, precio=1000.0)
    _setup_galeria_con_obras(session, "dash_b@test.com", "g-dash-b", n_obras=1, precio=500.0)

    headers_a = _login(client, "dash_a@test.com")
    headers_b = _login(client, "dash_b@test.com")

    stats_a = client.get("/dashboard/stats", headers=headers_a).json()
    stats_b = client.get("/dashboard/stats", headers=headers_b).json()

    # Totales aislados
    assert stats_a["total_obras"] == 3
    assert stats_b["total_obras"] == 1

    # Valores monetarios aislados (el leak más peligroso)
    assert stats_a["valor_inventario"] == 3000.0
    assert stats_b["valor_inventario"] == 500.0

    # Top técnicas aislado (el bug sutil del JOIN)
    nombres_a = [t["nombre"] for t in stats_a["top_tecnicas"]]
    nombres_b = [t["nombre"] for t in stats_b["top_tecnicas"]]
    assert "Téc g-dash-a" in nombres_a
    assert "Téc g-dash-a" not in nombres_b
    assert "Téc g-dash-b" in nombres_b
    assert "Téc g-dash-b" not in nombres_a

def test_dashboard_usuario_sin_galeria_recibe_403(client: TestClient, session: Session):
    """Un usuario sin galeria_id no puede ver métricas (403, no 500)."""
    usuario = Usuario(
        email="dash_sin_galeria@test.com",
        nombre="Sin Galería",
        password_hash=hash_password("password123"),
        rol=RolUsuario.ADMIN,
        galeria_id=None,
    )
    session.add(usuario)
    session.commit()

    headers = _login(client, "dash_sin_galeria@test.com")
    r = client.get("/dashboard/stats", headers=headers)
    assert r.status_code == 403