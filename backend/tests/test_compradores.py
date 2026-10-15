import uuid
from datetime import date
from fastapi.testclient import TestClient


def _crear_tecnica(client: TestClient) -> str:
    nombre = f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"})
    assert r.status_code == 201, r.json()
    return nombre


def _crear_obra(client: TestClient, tecnica_nombre: str, **overrides) -> dict:
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "precio": "1500",
        "estado": "disponible",
        "tecnica": tecnica_nombre,
    }
    data.update(overrides)
    r = client.post("/obras/", data=data)
    assert r.status_code == 201, r.json()
    return r.json()


def _crear_comprador(client: TestClient) -> dict:
    r = client.post("/compradores/", json={
        "nombre": f"Comprador {uuid.uuid4().hex[:8]}",
        "email": f"test{uuid.uuid4().hex[:8]}@example.com",
        "telefono": "11-2345-6789",
        "direccion": "Av. Test 123",
    })
    assert r.status_code == 201, r.json()
    return r.json()


def test_registrar_venta_cambia_estado_de_obra(client: TestClient):
    """Registrar una venta cambia el estado de la obra a 'vendida'."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)
    comprador = _crear_comprador(client)

    # Registrar venta usando el endpoint REAL: /compradores/ventas/registrar
    r = client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador["id"],
        "fecha_venta": date.today().isoformat(),
    })
    assert r.status_code == 201, r.json()

    # Verificar que la obra ahora está vendida
    obra_actualizada = client.get(f"/obras/{obra['id']}").json()
    assert obra_actualizada["estado"] == "vendida"
    assert obra_actualizada["comprador_id"] == comprador["id"]


def test_no_se_puede_vender_una_obra_ya_vendida(client: TestClient):
    """Una obra vendida no puede venderse de nuevo."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)
    comprador1 = _crear_comprador(client)
    comprador2 = _crear_comprador(client)

    # Primera venta
    r1 = client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador1["id"],
        "fecha_venta": date.today().isoformat(),
    })
    assert r1.status_code == 201

    # Intentar segunda venta: debe fallar (400 por lógica de negocio)
    r2 = client.post("/compradores/ventas/registrar", json={
        "obra_id": obra["id"],
        "comprador_id": comprador2["id"],
        "fecha_venta": date.today().isoformat(),
    })
    assert r2.status_code in (400, 409)