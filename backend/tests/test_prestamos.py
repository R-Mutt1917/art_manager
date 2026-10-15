import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient


def _crear_tecnica(client: TestClient) -> str:
    nombre = f"Técnica {uuid.uuid4().hex[:8]}"
    r = client.post("/tecnicas/", json={"nombre": nombre, "descripcion": "Test"})
    assert r.status_code == 201
    return nombre


def _crear_obra(client: TestClient, tecnica_nombre: str) -> dict:
    data = {
        "titulo": "Obra de prueba",
        "anio": "2024",
        "dimensiones": "50x70 cm",
        "estado": "disponible",
        "tecnica": tecnica_nombre,
    }
    r = client.post("/obras/", data=data)
    assert r.status_code == 201, r.json()
    return r.json()


def _crear_comprador_y_vender(client: TestClient, obra_id: int):
    """Helper: crea un comprador y vende la obra para forzar estado 'vendida'."""
    comprador = client.post("/compradores/", json={
        "nombre": f"Comprador {uuid.uuid4().hex[:8]}",
        "email": f"test{uuid.uuid4().hex[:8]}@example.com",
    }).json()
    client.post("/compradores/ventas/registrar", json={
        "obra_id": obra_id,
        "comprador_id": comprador["id"],
        "fecha_venta": date.today().isoformat(),
    })


def test_ciclo_completo_de_prestamo(client: TestClient):
    """Crear préstamo y registrar devolución."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)

    hoy = date.today()
    r = client.post("/prestamos/", json={
        "obra_id": obra["id"],
        "institucion_destino": f"Museo {uuid.uuid4().hex[:8]}",
        "prestatario_nombre": "Dr. Juan Pérez",             # ← obligatorio
        "fecha_prestamo": hoy.isoformat(),                  # ← obligatorio
        "fecha_devolucion_esperada": (hoy + timedelta(days=30)).isoformat(),  # ← obligatorio
        "motivo": "Exposición temporal",
    })
    assert r.status_code == 201, r.json()
    prestamo = r.json()

    # Verificar estado de la obra
    obra_actualizada = client.get(f"/obras/{obra['id']}").json()
    assert obra_actualizada["estado"] == "en_prestamo"

    # Registrar devolución: endpoint real es /devolucion (no /registrar-devolucion)
    r_dev = client.post(f"/prestamos/{prestamo['id']}/devolucion", json={
        "condicion_retorno": "excelente",
        "observaciones": "Sin daños",
        "fecha_devolucion_real": date.today().isoformat(),  # ← NUEVO: obligatorio
    })
    assert r_dev.status_code == 200, r_dev.json()

    # Obra queda disponible de nuevo
    obra_final = client.get(f"/obras/{obra['id']}").json()
    assert obra_final["estado"] == "disponible"


def test_no_se_puede_prestar_una_obra_vendida(client: TestClient):
    """Una obra vendida no puede ser prestada."""
    nombre_tecnica = _crear_tecnica(client)
    obra = _crear_obra(client, nombre_tecnica)

    # Vender la obra primero
    _crear_comprador_y_vender(client, obra["id"])

    # Intentar crear préstamo
    hoy = date.today()
    r = client.post("/prestamos/", json={
        "obra_id": obra["id"],
        "institucion_destino": "Museo Test",
        "prestatario_nombre": "Dr. X",
        "fecha_prestamo": hoy.isoformat(),
        "fecha_devolucion_esperada": (hoy + timedelta(days=30)).isoformat(),
        "motivo": "Préstamo",
    })
    # El endpoint debe rechazar con 400 (lógica de negocio) o 422 (validación)
    assert r.status_code in (400, 409, 422)