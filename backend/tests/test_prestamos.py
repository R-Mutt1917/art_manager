"""Tests del módulo de Préstamos."""
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


def _vender_obra(client: TestClient, obra_id: int, headers: dict = None) -> None:
    """Vende una obra (cambia estado a vendida)."""
    # Crear comprador
    r = client.post(
        "/compradores/",
        json={
            "nombre": f"Comprador {uuid.uuid4().hex[:8]}",
            "email": f"c_{uuid.uuid4().hex[:8]}@example.com",
        },
        headers=headers or {},
    )
    comprador_id = r.json()["id"]
    
    # Registrar venta
    client.post(
        "/compradores/ventas/registrar",
        json={
            "obra_id": obra_id,
            "comprador_id": comprador_id,
            "fecha_venta": "2024-12-01",
        },
        headers=headers or {},
    )


def test_ciclo_completo_de_prestamo(client: TestClient, auth_headers):
    """Crear préstamo y registrar devolución."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre_tecnica, headers=auth_headers)

    # Crear préstamo
    r = client.post(
        "/prestamos/",
        json={
            "obra_id": obra["id"],
            "prestatario_nombre": "Museo Nacional",
            "fecha_prestamo": "2025-01-01",
            "fecha_devolucion_esperada": "2025-06-01",
            "notas": "Exposición temporal",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()
    prestamo = r.json()

    # Verificar que el estado de la obra cambió a 'en_prestamo'
    r_obra = client.get(f"/obras/{obra['id']}")
    assert r_obra.json()["estado"] == "en_prestamo"

    # Registrar devolución
    r_dev = client.post(
        f"/prestamos/{prestamo['id']}/devolucion",
        json={
            "fecha_devolucion_real": "2025-05-30",
            "condicion_retorno": "Buena",
            "notas": "Devuelta en buen estado",
        },
        headers=auth_headers,
    )
    assert r_dev.status_code == 200, r_dev.json()

    # Verificar que la obra volvió a estar disponible
    r_obra = client.get(f"/obras/{obra['id']}")
    assert r_obra.json()["estado"] == "disponible"


def test_no_se_puede_prestar_una_obra_vendida(client: TestClient, auth_headers):
    """Una obra vendida no puede ser prestada."""
    nombre_tecnica = _crear_tecnica(client, headers=auth_headers)
    obra = _crear_obra(client, nombre_tecnica, headers=auth_headers)

    # Vender la obra
    _vender_obra(client, obra["id"], headers=auth_headers)

    # Intentar prestar (debe fallar)
    r = client.post(
        "/prestamos/",
        json={
            "obra_id": obra["id"],
            "prestatario_nombre": "Museo Nacional",
            "fecha_prestamo": "2025-01-01",
            "fecha_devolucion_esperada": "2025-06-01",
        },
        headers=auth_headers,
    )
    assert r.status_code == 400