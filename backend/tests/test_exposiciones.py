"""Tests del módulo de Exposiciones."""
import uuid
from fastapi.testclient import TestClient


def _crear_tecnica(client: TestClient, headers: dict = None, nombre: str | None = None) -> str:
    """Crea una técnica y devuelve su nombre."""
    nombre = nombre or f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"}, headers=headers or {})
    assert r.status_code == 201, r.json()
    return nombre


def _crear_obra(client: TestClient, tecnica_nombre: str, headers: dict = None, **overrides) -> dict:
    """Helper: crea una obra con FormData."""
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "estado": "disponible",
        "tecnica": tecnica_nombre,
    }
    data.update(overrides)
    r = client.post("/obras/", data=data, headers=headers or {})
    assert r.status_code == 201, r.json()
    return r.json()


def _crear_exposicion(client: TestClient, headers: dict = None, **overrides) -> dict:
    """Helper: crea una exposición."""
    data = {
        "nombre": f"Exposición {uuid.uuid4().hex[:8]}",
        "lugar": "Galería Test",
        "fecha_inicio": "2025-03-01",
        "fecha_fin": "2025-03-31",
    }
    data.update(overrides)
    r = client.post("/exposiciones/", json=data, headers=headers or {})
    assert r.status_code == 201, r.json()
    return r.json()


def test_asignar_obra_a_exposicion_sin_superposicion(client: TestClient, auth_headers):
    """Asignar una obra a una exposición sin conflictos de fechas."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre_tecnica, headers=auth_headers)
    expo = _crear_exposicion(client, headers=auth_headers)

    r = client.post(
        f"/exposiciones/{expo['id']}/obras/{obra['id']}",
        json={
            "fecha_ingreso": "2025-03-01",
            "fecha_retiro_esperada": "2025-03-31",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()


def test_rechazar_asignacion_con_fechas_superpuestas(client: TestClient, auth_headers):
    """No se puede asignar una obra si ya está en otra exposición en esas fechas."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre_tecnica, headers=auth_headers)
    
    expo1 = _crear_exposicion(
        client, 
        headers=auth_headers,
        nombre="Expo 1",
        fecha_inicio="2025-03-01",
        fecha_fin="2025-03-15"
    )
    expo2 = _crear_exposicion(
        client, 
        headers=auth_headers,
        nombre="Expo 2",
        fecha_inicio="2025-03-10",  # superposición
        fecha_fin="2025-03-25"
    )

    # Asignar a la primera expo (éxito)
    r1 = client.post(
        f"/exposiciones/{expo1['id']}/obras/{obra['id']}",
        json={
            "fecha_ingreso": "2025-03-01",
            "fecha_retiro_esperada": "2025-03-15",
        },
        headers=auth_headers,
    )
    assert r1.status_code == 201

    # Intentar asignar a la segunda expo (debe fallar)
    r2 = client.post(
        f"/exposiciones/{expo2['id']}/obras/{obra['id']}",
        json={
            "fecha_ingreso": "2025-03-10",
            "fecha_retiro_esperada": "2025-03-25",
        },
        headers=auth_headers,
    )
    assert r2.status_code == 400


def test_checklist_de_retiro(client: TestClient, auth_headers):
    """Verificar que la exposición genera un checklist de obras asignadas."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra1 = _crear_obra(client, nombre_tecnica, headers=auth_headers, titulo="Obra 1")
    obra2 = _crear_obra(client, nombre_tecnica, headers=auth_headers, titulo="Obra 2")
    expo = _crear_exposicion(client, headers=auth_headers)

    # Asignar ambas obras
    client.post(
        f"/exposiciones/{expo['id']}/obras/{obra1['id']}",
        json={"fecha_ingreso": "2025-03-01", "fecha_retiro_esperada": "2025-03-31"},
        headers=auth_headers,
    )
    client.post(
        f"/exposiciones/{expo['id']}/obras/{obra2['id']}",
        json={"fecha_ingreso": "2025-03-01", "fecha_retiro_esperada": "2025-03-31"},
        headers=auth_headers,
    )

    # Obtener checklist
    r = client.get(f"/exposiciones/{expo['id']}/checklist", headers=auth_headers)
    assert r.status_code == 200
    checklist = r.json()
    assert len(checklist) == 2