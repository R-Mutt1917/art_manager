"""Tests del módulo de Compradores y ventas."""
import uuid
from fastapi.testclient import TestClient


def _crear_tecnica(client: TestClient, headers: dict = None, nombre: str | None = None) -> str:
    """Crea una técnica y devuelve su nombre."""
    nombre = nombre or f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"}, headers=headers or {})
    assert r.status_code == 201, r.json()
    return nombre


def _crear_obra(client: TestClient, tecnica_nombre: str, headers: dict = None, **overrides) -> dict:
    """Helper: crea una obra con FormData y devuelve el JSON de respuesta."""
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "precio": "1500",
        "estado": "disponible",
        "tecnica": tecnica_nombre,
    }
    data.update(overrides)
    r = client.post("/obras/", data=data, headers=headers or {})
    assert r.status_code == 201, r.json()
    return r.json()


def _crear_comprador(client: TestClient, headers: dict = None, **overrides) -> dict:
    """Helper: crea un comprador."""
    data = {
        "nombre": f"Comprador {uuid.uuid4().hex[:8]}",
        "email": f"comprador_{uuid.uuid4().hex[:8]}@example.com",
        "telefono": "1234567890",
    }
    data.update(overrides)
    r = client.post("/compradores/", json=data, headers=headers or {})
    assert r.status_code == 201, r.json()
    return r.json()


def test_registrar_venta_cambia_estado_de_obra(client: TestClient, auth_headers):
    """Registrar una venta cambia el estado de la obra a 'vendida'."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre_tecnica, headers=auth_headers)
    comprador = _crear_comprador(client, headers=auth_headers)

    r = client.post(
        "/compradores/ventas/registrar",
        json={
            "obra_id": obra["id"],
            "comprador_id": comprador["id"],
            "fecha_venta": "2024-12-01",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()

    # Verificar que el estado de la obra cambió a 'vendida'
    r_obra = client.get(f"/obras/{obra['id']}")
    assert r_obra.json()["estado"] == "vendida"
    assert r_obra.json()["comprador_id"] == comprador["id"]


def test_no_se_puede_vender_una_obra_ya_vendida(client: TestClient, auth_headers):
    """Una obra vendida no puede venderse de nuevo."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre_tecnica, headers=auth_headers)
    comprador1 = _crear_comprador(client, headers=auth_headers)
    comprador2 = _crear_comprador(client, headers=auth_headers)

    # Primera venta (éxito)
    r1 = client.post(
        "/compradores/ventas/registrar",
        json={
            "obra_id": obra["id"],
            "comprador_id": comprador1["id"],
            "fecha_venta": "2024-12-01",
        },
        headers=auth_headers,
    )
    assert r1.status_code == 201

    # Segunda venta (debe fallar)
    r2 = client.post(
        "/compradores/ventas/registrar",
        json={
            "obra_id": obra["id"],
            "comprador_id": comprador2["id"],
            "fecha_venta": "2024-12-02",
        },
        headers=auth_headers,
    )
    assert r2.status_code == 400